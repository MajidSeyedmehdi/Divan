USE [divan_fanni]
GO
/****** Object:  StoredProcedure [dbo].[Sp_InsertSoundShiftAssignment]    Script Date: 1/1/2025 12:00:00 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:		<SMS,,Majid Seyedmehdi>
-- Create date: <2025/01/01,>
-- Description:	<Sp_InsertSoundShiftAssignment - Insert initial sound shift assignment>
-- =============================================
CREATE PROCEDURE [dbo].[Sp_InsertSoundShiftAssignment] 
    @id_sound_recorder INT,
    @id_shift INT,
    @id_network INT,
    @shift_date DATE,
    @shift_day NVARCHAR(50),
    @user_name NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        BEGIN TRANSACTION;
        
        DECLARE @new_id_sound_shift INT;

        -- Check if assignment already exists for the same date, shift, and network
        IF EXISTS (
            SELECT 1 FROM Tbl_Sound_Shift_Assignment 
            WHERE Shift_date = @shift_date 
            AND Id_shift = @id_shift 
            AND Id_network = @id_network 
            AND Active = 1 
            AND Del = 0
        )
        BEGIN
            -- Update existing assignment
            UPDATE Tbl_Sound_Shift_Assignment
            SET 
                Id_sound_recorder = @id_sound_recorder,
                Shift_day = @shift_day,
                Update_date = GETDATE()
            WHERE Shift_date = @shift_date 
            AND Id_shift = @id_shift 
            AND Id_network = @id_network 
            AND Active = 1 
            AND Del = 0;
            
            -- Get the existing ID
            SELECT @new_id_sound_shift = Id_sound_shift 
            FROM Tbl_Sound_Shift_Assignment 
            WHERE Shift_date = @shift_date 
            AND Id_shift = @id_shift 
            AND Id_network = @id_network 
            AND Active = 1 
            AND Del = 0;
        END
        ELSE
        BEGIN
            -- Insert new assignment
            INSERT INTO Tbl_Sound_Shift_Assignment (
                Id_sound_recorder, Id_shift, Id_network, Shift_date, Shift_day,
                Active, Del, Update_date
            )
            VALUES (
                @id_sound_recorder, @id_shift, @id_network, @shift_date, @shift_day,
                1, 0, GETDATE()
            );
            
            SET @new_id_sound_shift = SCOPE_IDENTITY();
        END

        COMMIT TRANSACTION;
        
        -- Return success message with new ID
        SELECT 
            'تخصیص شیفت با موفقیت ثبت شد' AS Message,
            @new_id_sound_shift AS Id_sound_shift;
            
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
            
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();
        
        -- Return error information
        SELECT 
            'خطا در ثبت تخصیص شیفت' AS Message,
            ERROR_NUMBER() AS ErrorNumber,
            @ErrorMessage AS ErrorMessage,
            ERROR_LINE() AS ErrorLine,
            ERROR_PROCEDURE() AS ErrorProcedure;
            
        RAISERROR(@ErrorMessage, @ErrorSeverity, @ErrorState);
    END CATCH
END
