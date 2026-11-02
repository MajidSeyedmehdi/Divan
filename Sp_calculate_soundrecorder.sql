USE [divan_fanni]
GO

/****** Object:  StoredProcedure [dbo].[Sp_Calculate_SoundRecorder_Payroll]    Script Date: 8/30/2026 8:19:54 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


CREATE PROCEDURE [dbo].[Sp_Calculate_SoundRecorder_Payroll]
    @PeriodId INT
AS
BEGIN
    SET NOCOUNT ON;

    /* =========================================================
       1. دریافت تاریخ شروع و پایان دوره مالی
       ========================================================= */
    DECLARE @StartDate DATE,
            @EndDate   DATE;

    SELECT
        @StartDate = Start_date,
        @EndDate   = End_date
    FROM Tbl_Financial_Period
    WHERE Id_period = @PeriodId;

    IF @StartDate IS NULL OR @EndDate IS NULL
    BEGIN
        RAISERROR(
            N'دوره مالی مورد نظر یافت نشد یا تاریخ‌های آن معتبر نیستند.',
            16,
            1
        );
        RETURN;
    END;


    /* =========================================================
       2. پاکسازی Temporary Table ها
       ========================================================= */
    IF OBJECT_ID('tempdb..#FinalResult') IS NOT NULL
        DROP TABLE #FinalResult;

    IF OBJECT_ID('tempdb..#Temp_Shift_Payroll_Calc') IS NOT NULL
        DROP TABLE #Temp_Shift_Payroll_Calc;

    IF OBJECT_ID('tempdb..#CalculatedShiftsStatus') IS NOT NULL
        DROP TABLE #CalculatedShiftsStatus;


    /* =========================================================
       3. وضعیت محاسباتی نهایی شیفت‌ها
       ========================================================= */
    CREATE TABLE #CalculatedShiftsStatus
    (
        Id_payrolcalc INT NULL,
        Shift_date DATE,
        Id_sound_recorder INT,
        Id_network INT,
        Id_shift INT,
        Id_shift_type INT,
        Is_holiday BIT,
        Total_rate DECIMAL(18,2),
        Special_shift BIT,
        Mandatory_shift BIT
    );


    /* =========================================================
       4. نتیجه نهایی هر صدابردار
       ========================================================= */
    CREATE TABLE #FinalResult
    (
        Id_sound_recorder INT,

        Total_Leaves INT,

        Initial_Total_Hours INT,
        Initial_Shifts_Count INT,

        Special_Shifts_Count INT,

        Deleted_Morning_Shifts INT,
        Deleted_Evening_Shifts INT,
        Deleted_Special_Shifts INT,

        Remaining_Total_Hours INT,
        Remaining_Shifts_Count INT,

        Final_Baraovard DECIMAL(18,2)
    );


    /* =========================================================
       5. دریافت تمام شیفت‌های دوره مالی
       ========================================================= */
    SELECT
        Id_calc,
        Shift_date,
        Id_sound_recorder,
        Id_network,
        Id_shift,
        Id_shift_type,
        Is_holiday,
        Total_rate,

        CASE
            WHEN Is_holiday = 1
                 OR Id_shift IN (3,10,11,12,13)
            THEN CAST(1 AS BIT)
            ELSE CAST(0 AS BIT)
        END AS Special_shift,

        CAST(0 AS BIT) AS Mandatory_shift

    INTO #Temp_Shift_Payroll_Calc

    FROM Tbl_Shift_Payroll_Calc

    WHERE Shift_date >= @StartDate
      AND Shift_date <= @EndDate;


    /* =========================================================
       6. متغیرها
       ========================================================= */
    DECLARE @CurrentRecorder INT;

    DECLARE @IsAssistantSoundRecorder BIT;

    DECLARE @TotalHoursRequired INT;
    DECLARE @LeaveDays INT;
    DECLARE @SpecialShiftsCount INT;

    DECLARE @NewDutyHours INT;

    DECLARE @InitialHours INT;
    DECLARE @InitialCount INT;

    DECLARE @DeletedMorning INT;
    DECLARE @DeletedEvening INT;
    DECLARE @DeletedSpecial INT;

    DECLARE @CurrentShiftId INT;
    DECLARE @CurrentShiftHours INT;
    DECLARE @CurrentShiftTypeId INT;

    DECLARE @MaxSpecialHoursAllowed INT;
    DECLARE @DeductedSpecialHours INT;

    DECLARE @RemainingHours INT;
    DECLARE @RemainingCount INT;
    DECLARE @Baraovard DECIMAL(18,2);


    /* =========================================================
       7. پیمایش صدابرداران
       ========================================================= */
    DECLARE Recorder_Cursor CURSOR LOCAL FAST_FORWARD FOR

        SELECT DISTINCT Id_sound_recorder
        FROM #Temp_Shift_Payroll_Calc;

    OPEN Recorder_Cursor;

    FETCH NEXT FROM Recorder_Cursor
    INTO @CurrentRecorder;


    WHILE @@FETCH_STATUS = 0
    BEGIN

        /* -----------------------------------------------------
           مقداردهی اولیه
           ----------------------------------------------------- */
        SET @TotalHoursRequired = 104;

        SET @LeaveDays = 0;

        SET @SpecialShiftsCount = 0;

        SET @NewDutyHours = 104;

        SET @InitialHours = 0;
        SET @InitialCount = 0;

        SET @DeletedMorning = 0;
        SET @DeletedEvening = 0;
        SET @DeletedSpecial = 0;

        SET @DeductedSpecialHours = 0;

        SET @RemainingHours = 0;
        SET @RemainingCount = 0;
        SET @Baraovard = 0;

        /* =====================================================
           تشخیص صدابردار کمکی

           فقط وجود حداقل یک مجوز فعال و غیرحذف‌شده
           با Permision_assistant_sound_recorder = 1 مهم است.
           داشتن مجوزهای دیگر مانعی ندارد.
           ===================================================== */
        SET @IsAssistantSoundRecorder = 0;

        IF EXISTS
        (
            SELECT 1
            FROM Tbl_Sound_Recorders sr
            INNER JOIN Tbl_Permisions p
                ON p.Id_personal = sr.Id_personal
            WHERE sr.Id_sound_recorder = @CurrentRecorder
              AND p.Permision_assistant_sound_recorder = 1
              AND p.Active = 1
              AND p.Del = 0
        )
        BEGIN
            SET @IsAssistantSoundRecorder = 1;
        END;


        /* =====================================================
           آمار اولیه
           برای همه افراد محاسبه می‌شود.
           ===================================================== */
        SELECT
            @InitialHours =
                ISNULL
                (
                    SUM
                    (
                        CASE
                            WHEN t.Id_shift IN (3,10,11,12,13)
                                THEN 4
                            ELSE st.Shift_type
                        END
                    ),
                    0
                ),

            @InitialCount = COUNT(*)

        FROM #Temp_Shift_Payroll_Calc t

        INNER JOIN tbl_Shift_Type st
            ON t.Id_shift_type = st.Id_shift_type

        WHERE t.Id_sound_recorder = @CurrentRecorder;


        /* =====================================================
           تعداد شیفت‌های ویژه
           ===================================================== */
        SELECT
            @SpecialShiftsCount = COUNT(*)

        FROM #Temp_Shift_Payroll_Calc

        WHERE Id_sound_recorder = @CurrentRecorder
          AND Special_shift = 1;


        /* =====================================================
           =====================================================
           مسیر اول: صدابردار کمکی
           =====================================================
           
           هیچ‌کدام از موارد زیر برای او اعمال نمی‌شود:
           
           - 104 ساعت موظفی
           - مرخصی
           - سقف 32 ساعت ویژه
           - کسر شیفت صبح/عصر
           - Mandatory_shift
           
           تمام شیفت‌های دوره، کامل برآورد می‌شوند.
           ===================================================== */
        IF @IsAssistantSoundRecorder = 1
        BEGIN

            /* -------------------------------------------------
               مرخصی فقط جهت نمایش در خروجی خوانده می‌شود
               و هیچ تأثیری روی مبلغ ندارد.
               ------------------------------------------------- */
            SELECT
                @LeaveDays = ISNULL(SUM(Leaves), 0)
            FROM tbl_leaves
            WHERE Id_sound_recorder = @CurrentRecorder
              AND Active = 1
              AND Del = 0
              AND Start_date >= @StartDate
              AND End_date <= @EndDate;


            /* -------------------------------------------------
               هیچ شیفتی موظفی نیست.
               همه Mandatory_shift = 0 باقی می‌مانند.

               مجموع ساعت تمام شیفت‌ها
               و مجموع مبلغ تمام شیفت‌ها = برآورد
               ------------------------------------------------- */
            SELECT
                @RemainingHours =
                    ISNULL
                    (
                        SUM
                        (
                            CASE
                                WHEN t.Id_shift IN (3,10,11,12,13)
                                    THEN 4
                                ELSE st.Shift_type
                            END
                        ),
                        0
                    ),

                @RemainingCount = COUNT(*),

                @Baraovard =
                    ISNULL(SUM(t.Total_rate), 0)

            FROM #Temp_Shift_Payroll_Calc t

            INNER JOIN tbl_Shift_Type st
                ON t.Id_shift_type = st.Id_shift_type

            WHERE t.Id_sound_recorder = @CurrentRecorder;


            /* -------------------------------------------------
               ثبت وضعیت همه شیفت‌ها
               Mandatory_shift = 0
               ------------------------------------------------- */
            INSERT INTO #CalculatedShiftsStatus
            (
                Id_payrolcalc,
                Shift_date,
                Id_sound_recorder,
                Id_network,
                Id_shift,
                Id_shift_type,
                Is_holiday,
                Total_rate,
                Special_shift,
                Mandatory_shift
            )

            SELECT
                Id_calc,
                Shift_date,
                Id_sound_recorder,
                Id_network,
                Id_shift,
                Id_shift_type,
                Is_holiday,
                Total_rate,
                Special_shift,
                CAST(0 AS BIT)

            FROM #Temp_Shift_Payroll_Calc

            WHERE Id_sound_recorder = @CurrentRecorder;


            /* -------------------------------------------------
               ثبت نتیجه صدابردار کمکی
               ------------------------------------------------- */
            INSERT INTO #FinalResult
            (
                Id_sound_recorder,
                Total_Leaves,
                Initial_Total_Hours,
                Initial_Shifts_Count,
                Special_Shifts_Count,
                Deleted_Morning_Shifts,
                Deleted_Evening_Shifts,
                Deleted_Special_Shifts,
                Remaining_Total_Hours,
                Remaining_Shifts_Count,
                Final_Baraovard
            )
            VALUES
            (
                @CurrentRecorder,
                @LeaveDays,
                @InitialHours,
                @InitialCount,
                @SpecialShiftsCount,
                0,
                0,
                0,
                @RemainingHours,
                @RemainingCount,
                @Baraovard
            );


            /* -------------------------------------------------
               رفتن سراغ صدابردار بعدی
               ------------------------------------------------- */
            FETCH NEXT FROM Recorder_Cursor
            INTO @CurrentRecorder;

            CONTINUE;
        END;


        /* =====================================================
           =====================================================
           مسیر دوم: صدابردار عادی
           =====================================================
           ===================================================== */


        /* =====================================================
           ب) محاسبه مرخصی فقط در همین دوره مالی
           ===================================================== */
        SELECT
            @LeaveDays = ISNULL(SUM(Leaves), 0)

        FROM tbl_leaves

        WHERE Id_sound_recorder = @CurrentRecorder
          AND Active = 1
          AND Del = 0
          AND Start_date >= @StartDate
          AND End_date <= @EndDate;


        /* -----------------------------------------------------
           104 - مرخصی × 8
           ----------------------------------------------------- */
        SET @NewDutyHours =
            @TotalHoursRequired - (@LeaveDays * 8);

        IF @NewDutyHours < 0
            SET @NewDutyHours = 0;


        /* =====================================================
           ج) اولویت اول:
              مصرف شیفت ویژه تا سقف 32 ساعت
           ===================================================== */
        SET @MaxSpecialHoursAllowed = 32;


        DECLARE Special_Shift_Cursor CURSOR LOCAL FAST_FORWARD FOR

            SELECT
                t.Id_calc,

                CASE
                    WHEN t.Id_shift IN (3,10,11,12,13)
                        THEN 4
                    ELSE st.Shift_type
                END

            FROM #Temp_Shift_Payroll_Calc t

            INNER JOIN tbl_Shift_Type st
                ON t.Id_shift_type = st.Id_shift_type

            WHERE t.Id_sound_recorder = @CurrentRecorder
              AND t.Special_shift = 1
              AND t.Mandatory_shift = 0

            ORDER BY
                t.Shift_date ASC,
                t.Id_calc ASC;


        OPEN Special_Shift_Cursor;

        FETCH NEXT FROM Special_Shift_Cursor
        INTO @CurrentShiftId, @CurrentShiftHours;


        WHILE @@FETCH_STATUS = 0
        BEGIN

            /*
               شیفت فقط در صورتی وارد موظفی می‌شود که:
               1- ساعتش از موظفی باقی‌مانده بیشتر نباشد
               2- مجموع ویژه موظفی از 32 بیشتر نشود
            */
            IF @NewDutyHours > 0
               AND @CurrentShiftHours <= @NewDutyHours
               AND (@DeductedSpecialHours + @CurrentShiftHours)
                    <= @MaxSpecialHoursAllowed
            BEGIN

                SET @NewDutyHours =
                    @NewDutyHours - @CurrentShiftHours;

                SET @DeductedSpecialHours =
                    @DeductedSpecialHours + @CurrentShiftHours;

                SET @DeletedSpecial =
                    @DeletedSpecial + 1;


                UPDATE #Temp_Shift_Payroll_Calc
                SET Mandatory_shift = 1
                WHERE Id_calc = @CurrentShiftId;

            END;


            FETCH NEXT FROM Special_Shift_Cursor
            INTO @CurrentShiftId, @CurrentShiftHours;

        END;


        CLOSE Special_Shift_Cursor;
        DEALLOCATE Special_Shift_Cursor;


        /* =====================================================
           د) اولویت دوم:
              مصرف شیفت‌های معمولی به صورت یکی در میان
              صبح / عصر

              صبح  : 1,4,5
              عصر  : 2,6,8

              تا وقتی هر دو گروه موجود هستند،
              یکی از صبح و یکی از عصر انتخاب می‌شود.

              اگر یکی از گروه‌ها زودتر تمام شود،
              از گروه دیگر ادامه داده می‌شود.
           ===================================================== */
        IF @NewDutyHours > 0
        BEGIN

            DECLARE Shift_Cursor CURSOR LOCAL FAST_FORWARD FOR

                WITH RankedShifts AS
                (
                    SELECT

                        t.Id_calc,

                        CASE
                            WHEN t.Id_shift IN (3,10,11,12,13)
                                THEN 4
                            ELSE st.Shift_type
                        END AS ShiftHours,

                        t.Id_shift,

                        t.Shift_date,

                        CASE
                            WHEN t.Id_shift IN (1,4,5)
                                THEN 1
                            ELSE 2
                        END AS ShiftGroup,

                        ROW_NUMBER() OVER
                        (
                            PARTITION BY
                                CASE
                                    WHEN t.Id_shift IN (1,4,5)
                                        THEN 1
                                    ELSE 2
                                END

                            ORDER BY
                                t.Shift_date ASC,
                                t.Id_calc ASC
                        ) AS GroupRank

                    FROM #Temp_Shift_Payroll_Calc t

                    INNER JOIN tbl_Shift_Type st
                        ON t.Id_shift_type = st.Id_shift_type

                    WHERE t.Id_sound_recorder = @CurrentRecorder

                      AND t.Special_shift = 0

                      AND t.Mandatory_shift = 0

                      AND t.Id_shift IN (1,2,4,5,6,8)
                )

                SELECT
                    Id_calc,
                    ShiftHours,
                    Id_shift

                FROM RankedShifts

                ORDER BY
                    GroupRank ASC,
                    ShiftGroup ASC;


            OPEN Shift_Cursor;

            FETCH NEXT FROM Shift_Cursor
            INTO
                @CurrentShiftId,
                @CurrentShiftHours,
                @CurrentShiftTypeId;


            WHILE @@FETCH_STATUS = 0
            BEGIN

                /*
                   اگر این شیفت کامل در موظفی جا شود،
                   آن را موظفی می‌کنیم.

                   اگر جا نشود، شیفت را دست نمی‌زنیم
                   و سراغ شیفت بعدی می‌رویم.
                */
                IF @CurrentShiftHours <= @NewDutyHours
                BEGIN

                    SET @NewDutyHours =
                        @NewDutyHours - @CurrentShiftHours;


                    /* صبح */
                    IF @CurrentShiftTypeId IN (1,4,5)
                    BEGIN
                        SET @DeletedMorning =
                            @DeletedMorning + 1;
                    END

                    /* عصر */
                    ELSE IF @CurrentShiftTypeId IN (2,6,8)
                    BEGIN
                        SET @DeletedEvening =
                            @DeletedEvening + 1;
                    END;


                    UPDATE #Temp_Shift_Payroll_Calc
                    SET Mandatory_shift = 1
                    WHERE Id_calc = @CurrentShiftId;

                END;


                FETCH NEXT FROM Shift_Cursor
                INTO
                    @CurrentShiftId,
                    @CurrentShiftHours,
                    @CurrentShiftTypeId;

            END;


            CLOSE Shift_Cursor;
            DEALLOCATE Shift_Cursor;

        END;


        /* =====================================================
           هـ) اولویت سوم:
           
              اگر هنوز موظفی باقی مانده و شیفت عادی کافی
              وجود نداشت، از شیفت ویژه باقی‌مانده استفاده شود.

              در این مرحله دیگر سقف 32 ساعت اعمال نمی‌شود.
           ===================================================== */
        IF @NewDutyHours > 0
        BEGIN

            DECLARE Remaining_Special_Cursor CURSOR LOCAL FAST_FORWARD FOR

                SELECT
                    t.Id_calc,

                    CASE
                        WHEN t.Id_shift IN (3,10,11,12,13)
                            THEN 4
                        ELSE st.Shift_type
                    END

                FROM #Temp_Shift_Payroll_Calc t

                INNER JOIN tbl_Shift_Type st
                    ON t.Id_shift_type = st.Id_shift_type

                WHERE t.Id_sound_recorder = @CurrentRecorder

                  AND t.Special_shift = 1

                  AND t.Mandatory_shift = 0

                ORDER BY
                    t.Shift_date ASC,
                    t.Id_calc ASC;


            OPEN Remaining_Special_Cursor;

            FETCH NEXT FROM Remaining_Special_Cursor
            INTO
                @CurrentShiftId,
                @CurrentShiftHours;


            WHILE @@FETCH_STATUS = 0
            BEGIN

                /*
                   اینجا فقط شرط جا شدن شیفت در موظفی باقی‌مانده
                   مهم است و محدودیت 32 ساعت نداریم.
                */
                IF @CurrentShiftHours <= @NewDutyHours
                BEGIN

                    SET @NewDutyHours =
                        @NewDutyHours - @CurrentShiftHours;

                    SET @DeletedSpecial =
                        @DeletedSpecial + 1;


                    UPDATE #Temp_Shift_Payroll_Calc
                    SET Mandatory_shift = 1
                    WHERE Id_calc = @CurrentShiftId;

                END;


                FETCH NEXT FROM Remaining_Special_Cursor
                INTO
                    @CurrentShiftId,
                    @CurrentShiftHours;

            END;


            CLOSE Remaining_Special_Cursor;
            DEALLOCATE Remaining_Special_Cursor;

        END;


        /* =====================================================
           و) اگر موظفی کامل نشده باشد:

              برآورد باید صفر باشد.
           ===================================================== */
        IF @NewDutyHours > 0
        BEGIN

            SET @RemainingHours = 0;
            SET @RemainingCount = 0;
            SET @Baraovard = 0;

        END
        ELSE
        BEGIN

            /* =================================================
               ز) محاسبه شیفت‌های باقی‌مانده = برآورد
               ================================================= */

            SELECT

                @RemainingHours =
                    ISNULL
                    (
                        SUM
                        (
                            CASE
                                WHEN t.Mandatory_shift = 0
                                THEN
                                    CASE
                                        WHEN t.Id_shift IN
                                             (3,10,11,12,13)
                                            THEN 4
                                        ELSE st.Shift_type
                                    END
                                ELSE 0
                            END
                        ),
                        0
                    ),

                @RemainingCount =
                    ISNULL
                    (
                        SUM
                        (
                            CASE
                                WHEN t.Mandatory_shift = 0
                                    THEN 1
                                ELSE 0
                            END
                        ),
                        0
                    ),

                @Baraovard =
                    ISNULL
                    (
                        SUM
                        (
                            CASE
                                WHEN t.Mandatory_shift = 0
                                    THEN t.Total_rate
                                ELSE 0
                            END
                        ),
                        0
                    )

            FROM #Temp_Shift_Payroll_Calc t

            INNER JOIN tbl_Shift_Type st
                ON t.Id_shift_type = st.Id_shift_type

            WHERE t.Id_sound_recorder = @CurrentRecorder;

        END;


        /* =====================================================
           ح) ثبت وضعیت نهایی شیفت‌های صدابردار عادی
           ===================================================== */
        INSERT INTO #CalculatedShiftsStatus
        (
            Id_payrolcalc,
            Shift_date,
            Id_sound_recorder,
            Id_network,
            Id_shift,
            Id_shift_type,
            Is_holiday,
            Total_rate,
            Special_shift,
            Mandatory_shift
        )

        SELECT
            Id_calc,
            Shift_date,
            Id_sound_recorder,
            Id_network,
            Id_shift,
            Id_shift_type,
            Is_holiday,
            Total_rate,
            Special_shift,
            Mandatory_shift

        FROM #Temp_Shift_Payroll_Calc

        WHERE Id_sound_recorder = @CurrentRecorder;


        /* =====================================================
           ط) ثبت نتیجه صدابردار عادی
           ===================================================== */
        INSERT INTO #FinalResult
        (
            Id_sound_recorder,
            Total_Leaves,
            Initial_Total_Hours,
            Initial_Shifts_Count,
            Special_Shifts_Count,
            Deleted_Morning_Shifts,
            Deleted_Evening_Shifts,
            Deleted_Special_Shifts,
            Remaining_Total_Hours,
            Remaining_Shifts_Count,
            Final_Baraovard
        )
        VALUES
        (
            @CurrentRecorder,
            @LeaveDays,
            @InitialHours,
            @InitialCount,
            @SpecialShiftsCount,
            @DeletedMorning,
            @DeletedEvening,
            @DeletedSpecial,
            @RemainingHours,
            @RemainingCount,
            @Baraovard
        );


        /* -----------------------------------------------------
           صدابردار بعدی
           ----------------------------------------------------- */
        FETCH NEXT FROM Recorder_Cursor
        INTO @CurrentRecorder;

    END;


    CLOSE Recorder_Cursor;
    DEALLOCATE Recorder_Cursor;


    /* =========================================================
       8. بروزرسانی وضعیت شیفت‌ها
       ========================================================= */
    MERGE INTO Tbl_Shift_Payroll_Calc AS Target

    USING #CalculatedShiftsStatus AS Source

    ON
    (
        Target.Id_calc = Source.Id_payrolcalc
        AND Source.Id_payrolcalc IS NOT NULL
    )

    WHEN MATCHED THEN

        UPDATE SET

            Target.Special_shift =
                Source.Special_shift,

            Target.Mandatory_shift =
                Source.Mandatory_shift,

            Target.Shift_date =
                Source.Shift_date,

            Target.Id_sound_recorder =
                Source.Id_sound_recorder,

            Target.Id_network =
                Source.Id_network,

            Target.Id_shift =
                Source.Id_shift,

            Target.Id_shift_type =
                Source.Id_shift_type,

            Target.Is_holiday =
                Source.Is_holiday,

            Target.Total_rate =
                Source.Total_rate;


    /* =========================================================
       9. خروجی نهایی
       ========================================================= */
    SELECT

        p.Last_name AS Last_name,

        p.First_name AS First_name,

        p.National_code AS National_code,

        o.Employment_id AS Employment_id,

        cj.Current_job AS Current_job,

        l.Levels AS Levels,

        jl.Job_relation AS Job_relation,

        fr.Total_Leaves AS Leaves,

        fr.Special_Shifts_Count AS Special_shift,

        fr.Initial_Total_Hours AS Total_hours,

        m.Mandatory_hours AS Mandatory_hours,

        sr.Id_sound_recorder AS Id_sound_recorder,

        fr.Total_Leaves AS Total_Leaves,

        fr.Initial_Shifts_Count AS Initial_Shifts_Count,

        fr.Initial_Total_Hours AS Initial_Total_Hours,

        fr.Deleted_Morning_Shifts AS Deleted_Morning_Shifts,

        fr.Deleted_Evening_Shifts AS Deleted_Evening_Shifts,

        fr.Deleted_Special_Shifts AS Deleted_Special_Shifts,

        fr.Remaining_Total_Hours AS Remaining_Total_Hours,

        fr.Remaining_Shifts_Count AS Remaining_Shifts_Count,

        fr.Final_Baraovard AS Baravord


    FROM #FinalResult fr

    INNER JOIN Tbl_Sound_Recorders sr
        ON fr.Id_sound_recorder = sr.Id_sound_recorder

    INNER JOIN Tbl_Personally p
        ON sr.Id_personal = p.Id_personal

    INNER JOIN Tbl_Official o
        ON sr.Id_official = o.Id_official

    INNER JOIN Tbl_Current_Job cj
        ON o.Id_current_job = cj.Id_current_job

    INNER JOIN Tbl_Levels l
        ON l.Id_levels = o.Id_current_job_level

    INNER JOIN Tbl_Job_Relation jl
        ON jl.Id_job_relation = o.Id_job_relation

    INNER JOIN Tbl_Mandatory_Hours m
        ON m.Id_mandatory_hours = o.Id_mandatory_hours
	order by p.Last_name;

    /* =========================================================
       10. پاکسازی
       ========================================================= */
    DROP TABLE #FinalResult;

    DROP TABLE #Temp_Shift_Payroll_Calc;

    DROP TABLE #CalculatedShiftsStatus;

END;
GO

