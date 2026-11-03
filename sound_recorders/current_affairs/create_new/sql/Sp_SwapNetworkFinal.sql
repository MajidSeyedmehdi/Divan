ALTER PROCEDURE [dbo].[Sp_SwapNetworkFinal]
    @p_FromSoundRecorderId INT,
    @p_ToSoundRecorderId   INT,
    @p_FromNetworkId       INT,
    @p_FromShiftId         INT,
    @p_ToNetworkId         INT,
    @p_ToShiftId           INT,
    @p_ShiftDate           DATE,
    @p_UserName            NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    BEGIN TRY
        IF @p_FromSoundRecorderId IS NULL OR @p_ToSoundRecorderId IS NULL
            THROW 51001, N'شناسه صدابردارها معتبر نیست.', 1;

        IF @p_FromSoundRecorderId = @p_ToSoundRecorderId
            THROW 51002, N'صدابردار هر دو شیفت یکسان است.', 1;

        IF @p_FromNetworkId = @p_ToNetworkId AND @p_FromShiftId = @p_ToShiftId
            THROW 51003, N'شیفت مبدأ و مقصد یکسان است.', 1;

        BEGIN TRANSACTION;

        DECLARE @FromCount INT, @ToCount INT;
        DECLARE @ActualFromRecorderId INT, @ActualToRecorderId INT;

        SELECT
            @FromCount = COUNT(*),
            @ActualFromRecorderId = MIN(Id_sound_recorder)
        FROM dbo.Tbl_Sound_Shift_Final WITH (UPDLOCK, HOLDLOCK)
        WHERE Id_network = @p_FromNetworkId
          AND Id_shift = @p_FromShiftId
          AND Shift_date = @p_ShiftDate
          AND Active = 1 AND Del = 0;

        SELECT
            @ToCount = COUNT(*),
            @ActualToRecorderId = MIN(Id_sound_recorder)
        FROM dbo.Tbl_Sound_Shift_Final WITH (UPDLOCK, HOLDLOCK)
        WHERE Id_network = @p_ToNetworkId
          AND Id_shift = @p_ToShiftId
          AND Shift_date = @p_ShiftDate
          AND Active = 1 AND Del = 0;

        IF @FromCount <> 1 OR @ToCount <> 1
            THROW 51004, N'برای هر دو شیفت باید دقیقاً یک رکورد فعال وجود داشته باشد.', 1;

        IF @ActualFromRecorderId <> @p_FromSoundRecorderId
           OR @ActualToRecorderId <> @p_ToSoundRecorderId
            THROW 51005, N'اطلاعات شیفت‌ها هم‌زمان تغییر کرده است؛ صفحه را تازه‌سازی و دوباره تلاش کنید.', 1;

        UPDATE dbo.Tbl_Sound_Shift_Final
        SET Id_sound_recorder = @p_ToSoundRecorderId,
            Update_date = SYSDATETIMEOFFSET(),
            User_name = @p_UserName
        WHERE Id_network = @p_FromNetworkId
          AND Id_shift = @p_FromShiftId
          AND Shift_date = @p_ShiftDate
          AND Id_sound_recorder = @p_FromSoundRecorderId
          AND Active = 1 AND Del = 0;

        IF @@ROWCOUNT <> 1
            THROW 51006, N'به‌روزرسانی شیفت مبدأ انجام نشد.', 1;

        UPDATE dbo.Tbl_Sound_Shift_Final
        SET Id_sound_recorder = @p_FromSoundRecorderId,
            Update_date = SYSDATETIMEOFFSET(),
            User_name = @p_UserName
        WHERE Id_network = @p_ToNetworkId
          AND Id_shift = @p_ToShiftId
          AND Shift_date = @p_ShiftDate
          AND Id_sound_recorder = @p_ToSoundRecorderId
          AND Active = 1 AND Del = 0;

        IF @@ROWCOUNT <> 1
            THROW 51007, N'به‌روزرسانی شیفت مقصد انجام نشد.', 1;

        COMMIT TRANSACTION;
        SELECT 1 AS Status, N'جابه‌جایی با موفقیت انجام شد.' AS Message;
    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0
            ROLLBACK TRANSACTION;

        SELECT 0 AS Status, ERROR_MESSAGE() AS Message;
    END CATCH
END;
