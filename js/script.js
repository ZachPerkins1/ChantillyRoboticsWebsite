$(document).ready(function(){
  if($("#about-first").length!=0){ //So it only runs on the one page
    $(".subtitle").click(function(){
      $(this).next().slideToggle(300); //Goes inside the contentbox, finds all p's, get's the second (index 1)
    });
  }
  //Note: The load functions will not load local files in Chrome, Internet Explorer, or Edge.
  //They should work when the files are remote hosted though.
  //If you want to see the header and footer loaded on local, use Firefox.
  $("#header").load("header.html #header-body", function() {
    $("#navbar a").each(function() {
      if($(this).attr("href") == location.href.split("/").slice(-1)) {
        $(this).addClass("active");
        return false;
      }
    });
  });
  $("#footer").load("footer.html #footer-body");
  //TIMER STUFF//
  var endDate = new Date("Feb 21, 2017 23:59:59").getTime();

  //Do it once so it doesn't start empty
  var currDate = new Date().getTime();
  var distance = endDate-currDate;
  var days = Math.floor(distance / (1000 * 60 * 60 * 24));
  var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
  var seconds = Math.floor((distance % (1000 * 60)) / 1000);

  $("#days").html(days);
  $("#hours").html(hours);
  $("#minutes").html(minutes);
  $("#seconds").html(seconds);

  var resetTime = setInterval(function(){
    currDate = new Date().getTime();
    distance = endDate-currDate;
    days = Math.floor(distance / (1000 * 60 * 60 * 24));
    hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    seconds = Math.floor((distance % (1000 * 60)) / 1000);

    $("#days").html(days);
    $("#hours").html(hours);
    $("#minutes").html(minutes);
    $("#seconds").html(seconds);

  }, 1000); //Every second
});
