USE [divan_fanni]
GO
/****** Object:  StoredProcedure [dbo].[Sp_UpdateFinancialInformation]    Script Date: 7/27/2025 3:17:32 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:		<SMS,,Majid Seyedmehdi>
-- Create date: <2025/07/27,>
-- Description:	<Sp_UpdateFinancialInformation - Insert or Update Financial Information>
-- =============================================
CREATE PROCEDURE [dbo].[Sp_UpdateFinancialInformation] 
    @id_financial INT = NULL,
    @id_personal INT,
    @salary_base BIGINT = 0,
    @id_insurance_type INT = NULL,
    @insurance_number NVARCHAR(50) = NULL,
    @housing_right BIGINT = 0,
    @children_right BIGINT = 0,
    @kharobar BIGINT = 0,
    @sanavat BIGINT = 0,
    @eydi BIGINT = 0,
    @f_shoghl BIGINT = 0,
    @f_mohandesi BIGINT = 0,
    @f_abohava BIGINT = 0,
    @f_mahroomiat BIGINT = 0,
    @f_isargari BIGINT = 0,
    @f_51 BIGINT = 0,
    @f_sakhti_kar BIGINT = 0,
    @f_marzi BIGINT = 0,
    @f_enteghal BIGINT = 0,
    @f_jazb_mahroom BIGINT = 0,
    @management_right BIGINT = 0,
    @f_resaneh BIGINT = 0,
    @financial_user_name NVARCHAR(50),
    
    -- Tbl_Accounting parameters
    @id_bank INT = NULL,
    @account_number NVARCHAR(50) = NULL,
    @sheba_number NVARCHAR(50) = NULL,
    @accounting_user_name NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        BEGIN TRANSACTION;
        
        DECLARE @new_id_financial INT;
        DECLARE @new_id_account INT;

        -- Check if financial record exists
        IF @id_financial IS NOT NULL AND EXISTS (SELECT 1 FROM Tbl_Financial WHERE Id_financial = @id_financial)
        BEGIN
            -- UPDATE existing financial record
            UPDATE Tbl_Financial
            SET 
                Id_personal = @id_personal,
                salary_base = @salary_base,
                Id_insurance_type = @id_insurance_type,
                Insurance_number = @insurance_number,
                Housing_right = @housing_right,
                Children_right = @children_right,
                Kharobar = @kharobar,
                Sanavat = @sanavat,
                Eydi = @eydi,
                F_shoghl = @f_shoghl,
                F_mohandesi = @f_mohandesi,
                F_abohava = @f_abohava,
                F_mahroomiat = @f_mahroomiat,
                F_Isargari = @f_isargari,
                F_51 = @f_51,
                F_sakhti_kar = @f_sakhti_kar,
                F_marzi = @f_marzi,
                F_enteghal = @f_enteghal,
                F_jazb_mahroom = @f_jazb_mahroom,
                Management_right = @management_right,
                F_resaneh = @f_resaneh,
                User_name = @financial_user_name,
                Update_date = GETDATE()
            WHERE Id_financial = @id_financial;
            
            SET @new_id_financial = @id_financial;
        END
        ELSE
        BEGIN
            -- INSERT new financial record
            INSERT INTO Tbl_Financial (
                Id_personal, salary_base, Id_insurance_type, Insurance_number,
                Housing_right, Children_right, Kharobar, Sanavat, Eydi,
                F_shoghl, F_mohandesi, F_abohava, F_mahroomiat, F_Isargari,
                F_51, F_sakhti_kar, F_marzi, F_enteghal, F_jazb_mahroom,
                Management_right, F_resaneh, Active, Del, User_name, Update_date
            )
            VALUES (
                @id_personal, @salary_base, @id_insurance_type, @insurance_number,
                @housing_right, @children_right, @kharobar, @sanavat, @eydi,
                @f_shoghl, @f_mohandesi, @f_abohava, @f_mahroomiat, @f_isargari,
                @f_51, @f_sakhti_kar, @f_marzi, @f_enteghal, @f_jazb_mahroom,
                @management_right, @f_resaneh, 1, 0, @financial_user_name, GETDATE()
            );
            
            SET @new_id_financial = SCOPE_IDENTITY();
        END

        -- Handle bank account information if provided
        IF @id_bank IS NOT NULL AND @account_number IS NOT NULL
        BEGIN
            -- Check if change_password record exists for this financial record
            IF EXISTS (SELECT 1 FROM Tbl_Accounting WHERE Id_financial = @new_id_financial)
            BEGIN
                -- UPDATE existing change_password record
                UPDATE Tbl_Accounting
                SET 
                    Id_bank = @id_bank,
                    Account_number = @account_number,
                    Sheba_number = @sheba_number,
                    User_name = @accounting_user_name,
                    Update_date = GETDATE()
                WHERE Id_financial = @new_id_financial;
            END
            ELSE
            BEGIN
                -- INSERT new change_password record
                INSERT INTO Tbl_Accounting (
                    Id_financial, Id_bank, Account_number, Sheba_number,
                    Active, Del, User_name, Update_date
                )
                VALUES (
                    @new_id_financial, @id_bank, @account_number, @sheba_number,
                    1, 0, @accounting_user_name, GETDATE()
                );
                
                SET @new_id_account = SCOPE_IDENTITY();
            END
        END

        COMMIT TRANSACTION;
        
        -- Return the financial ID
        SELECT @new_id_financial AS Id_financial;
        
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
            
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();
        
        RAISERROR(@ErrorMessage, @ErrorSeverity, @ErrorState);
    END CATCH
END 