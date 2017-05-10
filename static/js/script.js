$(document).ready(function(){
  function setCountdownTimer(end) {
    var elapsed = end - new Date().getTime();
    if(elapsed <= 0) {
      $("#seconds").html("0s");
      clearInterval(resetTime);
      return;
    }
    var days = Math.floor(elapsed / (24 * 60 * 60 * 1000));
    var hours = Math.floor((elapsed % (24 * 60 * 60 * 1000)) / (60 * 60 * 1000));
    var minutes = Math.floor((elapsed % (60 * 60 * 1000)) / (60 * 1000));
    var seconds = Math.floor((elapsed % (60 * 1000)) / 1000);
    $("#days").html(days + "d");
    $("#hours").html(hours + "h");
    $("#minutes").html(minutes + "m");
    $("#seconds").html(seconds + "s");
    //stop displaying unneeded units
    if(days == 0) {
      $("#days").html("");
      if(hours == 0) {
        $("#hours").html("");
        if(minutes == 0) {
          $("#minutes").html("");
        }
      }
    }
  }
  //Do it once so it doesn't start empty
  setCountdownTimer(endDate);
  var resetTime = setInterval(function(){
    setCountdownTimer(endDate);
  }, 1000); //Every second
  //end timer stuff
  //
  //put mobile-specific (or desktop-specific) code here
  //
  function onMobileChange(query) {
    //mobile
    if(query.matches) {
      $(".subtitle").next().hide();
      $(".subtitle").click(function() {
        $(this).next().slideToggle(300);
      });
      $(".desktop-only").hide(); //elements we want only on desktop
      $(".mobile-only").show();
    //desktop
    } else {
      $(".subtitle").next().show();
      $(".subtitle").off("click");
      $(".desktop-only").show();
      $(".mobile-only").hide(); //elements we want only on mobile
    }
  }
  var media = window.matchMedia("screen and (max-width: 1000px)");
  media.addListener(onMobileChange);
  onMobileChange(media);
  //end mobile/desktop specific code
});
