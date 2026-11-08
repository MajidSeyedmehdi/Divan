/*
    تغییر وضعیت پرداخت برنامه زنده فقط در بازه تاریخ انتخاب‌شده.
    TargetStatus = 2: ثبت‌شده -> در انتظار پرداخت
    TargetStatus = 1: در انتظار پرداخت -> ثبت‌شده
*/
CREATE OR ALTER PROCEDURE dbo.Sp_Update_Live_Payment_Status_By_Period
    @Id_manual_program INT,
    @StartDate DATE,
    @EndDate DATE,
    @TargetStatus TINYINT,
    @UserName NVARCHAR(256)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    IF @Id_manual_program IS NULL
       OR @StartDate IS NULL
       OR @EndDate IS NULL
       OR @StartDate > @EndDate
       OR @TargetStatus NOT IN (1, 2)
    BEGIN
        THROW 50001, N'پارامترهای تغییر وضعیت پرداخت معتبر نیستند.', 1;
    END;

    DECLARE @SourceStatus TINYINT =
        CASE WHEN @TargetStatus = 2 THEN 1 ELSE 2 END;
    DECLARE @ChangedCount INT = 0;

    BEGIN TRY
        BEGIN TRANSACTION;

        UPDATE live
        SET
            live.Id_live_payment_status = @TargetStatus,
            live.Update_date = SYSDATETIMEOFFSET(),
            live.User_name = @UserName
        FROM dbo.Tbl_Sound_Shift_Live AS live
        WHERE live.Id_manual_program = @Id_manual_program
          AND live.Active = 1
          AND live.Del = 0
          AND live.Id_live_payment_status = @SourceStatus
          AND live.Live_shift_date >= @StartDate
          AND live.Live_shift_date < DATEADD(DAY, 1, @EndDate)
          AND EXISTS
          (
              SELECT 1
              FROM dbo.Tbl_Program_Sound_Spec AS spec
              WHERE spec.Id_manual_program = live.Id_manual_program
                AND spec.Active = 1
                AND spec.Del = 0
                AND NULLIF(LTRIM(RTRIM(spec.Code)), '') IS NOT NULL
          );

        SET @ChangedCount = @@ROWCOUNT;

        COMMIT TRANSACTION;

        SELECT @ChangedCount AS ChangedCount;
    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0
            ROLLBACK TRANSACTION;
        THROW;
    END CATCH;
END;
