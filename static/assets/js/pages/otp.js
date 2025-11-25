$(document).ready(function(){

    // Validate a field/input
    function validateField(elem) {
        const val = elem.val();
        const parent = elem.parents(".form-group");

        parent.find(".help-block").html("");
        const title = elem.attr("title");
        error = false;

        if (elem.prop("required") && !parent.hasClass("d-none")) {
            if (val == "") {
                message = "<p>وارد کردن " + title + "  اجباری است.</p>";
                parent.find(".help-block").append(message);
                error = true;
            }
        }

        if (elem.attr("id") === "txtCellphone" && val.length > 0) {
            if(! /^09\d{9}|^9\d{9}$/.test(val)){
                message = "<p>شماره همراه نادرست است، مثال: 09123456789.</p>";
                parent.find(".help-block").append(message);
                error = true;
            }
        }

        if (elem.attr("id") === "txtCode" && val.length > 0) {
            if(! /^\d{5}$/.test(val)){
                message = "<p>کد پنج رقمی ارسال شده با شماره همراه را دقیقا وارد کنید.</p>";
                parent.find(".help-block").append(message);
                error = true;
            }
        }

        if (error) {
            parent.addClass("has-error");
            return false;
        } else {
            parent.removeClass("has-error");
            parent.find(".help-block").html("");
            return true;
        }
    }


    // Handle submit button
    $("#btnSubmit").click(function(){
        if($(".row-sms").hasClass("d-none")){
            if (validateField($("#txtCellphone"))) {
                $("#txtCellphone").attr("readonly", "readonly");
                $("#mainAlert").text("رمز ورود به شماره همراه شما پیامک شد");
                $(".row-sms").removeClass("d-none");
                $("#txtCode").focus();
                ticker();
            }
        }else{
            if (validateField($("#txtCode"))){
                window.location.href = "dashboard.html";
            }
        }
    });


    // Click button when enter press in inputs
    $("#txtCellphone, #txtCode").on("keydown", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            $("#btnSubmit").click();
        }
    });


    // Resend sms timer
    function ticker(){
        let remainSeconds = 120;
        intervalId = setInterval((function () {
            if(remainSeconds<=0){
                $("#btnResendSms").removeClass("d-none");
                $("#otpTickerBox").addClass("d-none");
                clearInterval(intervalId);
            }else{
                let minutes = Math.floor(remainSeconds/60);
                let seconds = remainSeconds % 60;

                if(minutes<10){
                    minutes = "0" + minutes;
                }
                if(seconds<10){
                    seconds = "0" + seconds;
                }

                $("#minutes").text(minutes);
                $("#seconds").text(seconds);

                remainSeconds--;
            }
        }), 1000);
    }
});