$(document).ready(function(){
  if($("#about-first").length!=0){ //So it only runs on the one page
    //Hide all subtitle contents at first
    $(".content-box").find("p").next().hide();
    //show contents when headers are clicked
    $(".subtitle").click(function(){
      $(this).next().slideToggle(300); //Goes inside the contentbox, finds all p's, get's the second (index 1)
    });
  }
  //Note: The load functions will not load local files in Chrome, Internet Explorer, or Edge.
  //They should work when the files are remote hosted though.
  //If you want to see the header and footer loaded on local, use Firefox.
  $("#header").load("header.html #header-body", function() {
    //Returns the rightmost file/directory name sans page anchor and queries
    var page = location.href.split("/").slice(-1)[0].split(/#|\?/, 1)[0];
    if(page == "" || page == "612-Website"){ //Second case is if the page loaded is .../612-Website with no ending slash, just in case
      $("#navbar a[href='index.html']").addClass("active"); //Finds anchor element with reference to index.html
      return false; //No need to check the rest
    }
    $("#navbar a").each(function() {
      if($(this).attr("href") == page) {
        $(this).addClass("active");
        return false;
      }
    });
  });
  $("#footer").load("footer.html #footer-body");
  //TIMER STUFF
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

  var endDate = new Date("Feb 21, 2017 23:59:59").getTime();
  //  new Date().getTime() + (3 * 1000) + 3000;

  //Do it once so it doesn't start empty
  setCountdownTimer(endDate);
  var resetTime = setInterval(function(){
    setCountdownTimer(endDate);
  }, 1000); //Every second
//Konami Code
var count = 0;
//perhaps we can put this server-side and request?
var splashes = ["Not verified for the 3DS browser!", "Have you seen the marvelous breadfish?", "Shovel the fries!", "blurred_fruits.jpg", "All day every day!", "All hail the compiler!", "Thank the dealer!", "Sixty-one who?", "#define AWESOMENESS", "if(Boolean.toString(condition).equals(\"true\")"]
document.addEventListener('keydown',function(event){
  switch(event.keyCode){
    case 38:
      if(count==0||count==1)count++; //Up arrow
      else count=0;
      break;
    case 40:
      if(count==2||count==3)count++; //Down arrow
      else count=0;
      break;
    case 37:
      if(count==4||count==6)count++; //Left Arrow
      else count=0;
      break;
    case 39:
      if(count==5||count==7)count++; //Right arrow
      else count=0;
      break;
    case 66:
      if(count==8)count++; //B
      else count=0;
      break;
    case 65:
      if(count==9)count++; //A
      else count = 0;
      break;
    case 13:
      if(count==10){ //Enter
        $("#content").load("memes.html", function() {
          $("#meme-splash").html("(" + splashes[Math.floor(Math.random() * splashes.length)] + ")");
        });
      }
    default:
      count = 0;
  }
});
});
