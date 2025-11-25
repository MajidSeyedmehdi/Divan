USE [divan_fanni]
GO
/****** Object:  StoredProcedure [dbo].[Sp_InsertPersonalInformation]    Script Date: 6/28/2025 9:19:46 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:		<SMS,,Majid Seyedmehdi>
-- Create date: <2025/06/13,>
-- Description:	<Sp_InsertPersonalInformation>
-- =============================================
ALTER PROCEDURE [dbo].[Sp_InsertPersonalInformation] 
	-- Add the parameters for the stored procedure here
-- Tbl_Personally parameters
    @first_name NVARCHAR(50),
    @last_name NVARCHAR(50),
    @father_name NVARCHAR(50),
	@birth_number NVARCHAR(10),
    @national_code NVARCHAR(10),
    @birth_date NVARCHAR(50), 
	@birth_city NVARCHAR(20),
    @gender_status NVARCHAR(20),
    @marital_status NVARCHAR(20),
	@email NVARCHAR(50),
    @personal_user_name NVARCHAR(50),

    -- Tbl_Location parameters
    @postal_code NVARCHAR(10),
    @city NVARCHAR(50),
    @address NVARCHAR(200),
    @location_user_name NVARCHAR(50),

    -- Tbl_Education parameters
    @field_study NVARCHAR(100),
	@educational_level_name NVARCHAR(100),  -- Changed from @Id_educational_level int to @educational_level_name NVARCHAR(100)
    @university NVARCHAR(50),
    @education_user_name NVARCHAR(50),

    -- Tbl_Phone parameters
    @mobile_number NVARCHAR(11),
    @phone_number NVARCHAR(11) = NULL,
    @phone_user_name NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        BEGIN TRANSACTION;
        
        DECLARE @id_personal INT;
        DECLARE @id_location INT;
        DECLARE @id_education INT;
        DECLARE @id_phone INT;
        DECLARE @id_educational_level INT;  -- New variable to store the looked up ID

        -- Look up educational level ID by name
        SELECT @id_educational_level = Id_educational_level 
        FROM Tbl_Educational_level 
        WHERE Educational_level = @educational_level_name 
        AND Active = 1 
        AND Del = 0;

        -- If educational level not found, you can either:
        -- 1. Use a default value
        -- 2. Raise an error
        -- 3. Set to NULL
        IF @id_educational_level IS NULL
        BEGIN
            -- Option 1: Use default educational level (ID = 1)
            SELECT @id_educational_level = Id_educational_level 
            FROM Tbl_Educational_level 
            WHERE Id_educational_level = 1 
            AND Active = 1 
            AND Del = 0;
            
            -- If still NULL, set to NULL (will cause foreign key error if the column doesn't allow NULL)
            -- You can change this behavior as needed
        END

        -- Insert into Tbl_Personally
        INSERT INTO Tbl_Personally (
            First_name, Last_name, Father_name,Birth_number,National_code,
            Birth_date,Birth_city, Gender_status, Marital_status,Email,
            Active, Del, User_name, Update_date
        )
        VALUES (
            @first_name, @last_name, @father_name,@birth_number ,@national_code,
            @birth_date,@birth_city, @gender_status, @marital_status,@email,
            1, 0, @personal_user_name, GETDATE()
        );
        
        SET @id_personal = SCOPE_IDENTITY();

        -- Insert into Tbl_Location
        INSERT INTO Tbl_Location (
            Id_personal, Postal_code, City, Address,
            Active, Del, User_name, Update_date
        )
        VALUES (
            @id_personal, @postal_code, @city, @address,
            1, 0, @location_user_name, GETDATE()
        );

        SET @id_location = SCOPE_IDENTITY();

        -- Insert into Tbl_Education
        INSERT INTO Tbl_Education (
            Id_personal, Field_study,Id_educational_level, University,
            Active, Del, User_name, Update_date
        )
        VALUES (
            @id_personal, @field_study, @id_educational_level, @university,  -- Use the looked up ID
            1, 0, @education_user_name, GETDATE()
        );

        SET @id_education = SCOPE_IDENTITY();

        -- Insert into Tbl_Phone
        INSERT INTO Tbl_Phone (
            Id_personal, Mobile_number, Phone_number,
            Active, Del, User_name, Update_date
        )
        VALUES (
            @id_personal, @mobile_number, @phone_number,
            1, 0, @phone_user_name, GETDATE()
        );

        SET @id_phone = SCOPE_IDENTITY();
        
        COMMIT TRANSACTION;
        
        -- Return the new IDs
        SELECT 
			'اطلاعات شخصی با موفقیت ثبت شد' AS Message,
            @id_personal AS NewPersonalID,
            @id_location AS NewLocationID,
            @id_education AS NewEducationID,
            @id_phone AS NewPhoneID;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
            
        -- Return error information
        SELECT 
            ERROR_NUMBER() AS ErrorNumber,
            ERROR_MESSAGE() AS ErrorMessage,
            ERROR_LINE() AS ErrorLine,
            ERROR_PROCEDURE() AS ErrorProcedure;
            
        THROW;
    END CATCH;
END 