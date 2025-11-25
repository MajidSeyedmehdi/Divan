USE [divan_fanni]
GO
/****** Object:  StoredProcedure [dbo].[Sp_GetSoundShiftAssignmentsByMonth]    Script Date: 2025-09-30 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:        <SMS, Majid Seyedmehdi>
-- Create date:   <2025/09/30>
-- Description:   Returns rows from Tbl_Sound_Shift_Assignment by @id_network and Gregorian @year/@month
-- =============================================
CREATE OR ALTER PROCEDURE [dbo].[Sp_GetSoundShiftAssignmentsByMonth]
    @id_network INT,
    @year INT,
    @month INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        ssa.Id_sound_shift,
        ssa.Id_sound_recorder,
        ssa.Id_shift,
        ssa.Id_network,
        ssa.Shift_date,
        ssa.Shift_day
    FROM Tbl_Sound_Shift_Assignment AS ssa
    WHERE ssa.Id_network = @id_network
      AND YEAR(ssa.Shift_date) = @year
      AND MONTH(ssa.Shift_date) = @month
      AND (ssa.Active = 1 OR ssa.Active IS NULL)
      AND (ssa.Del = 0 OR ssa.Del IS NULL)
    ORDER BY ssa.Shift_date, ssa.Id_shift;
END
