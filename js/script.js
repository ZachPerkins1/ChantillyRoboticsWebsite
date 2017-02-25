$(document).ready(function(){
  //Note: The load functions will not load local files in Chrome, Internet Explorer, or Edge.
  //They should work when the files are remote hosted though.
  //If you want to see the header and footer loaded on local, use Firefox.
  $("#header").load("header.html", function() {
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
  $("#footer").load("footer.html");
  //events
  $.get("events.json", function(data) {
    var now = new Date();
    //take the first 20 events that happen in the future
    for(var i in data) {
      var dt = new Date(data[i].date);
      if(dt >= now) {
        data = data.slice(i, i + 20);
        break;
      }
    }
    setEvents(data);
    setCountdown(data[0]);
  }, "json");
  function setEvents(events) {
    var ev = $("#events");
    for(var i in events) {
      ev.append(
      '<tr class="' + (i % 2 == 0 ? 'entry' : '') + '">\
         <td class="evname"></td>\
         <td class="evdate"></td>\
         <td class="evloc"></td>\
       </tr>');
    }
    var evname = $("#events .evname");
    var evdate = $("#events .evdate");
    var evloc = $("#events .evloc");
    for(var i in events) {
      evname.eq(i).text(events[i].name);
      evdate.eq(i).text(events[i].date.slice(0, -9)); //hacky string code
      evloc.eq(i).text(events[i].where);
    }
  }
  //end events
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
  function setCountdown(to) {
    var endDate = new Date(to.date).getTime();
    $("#countdown-desc").text(to.name);
    //Do it once so it doesn't start empty
    setCountdownTimer(endDate);
    var resetTime = setInterval(function(){
      setCountdownTimer(endDate);
    }, 1000); //Every second
  }
  //end timer stuff
  //put mobile-specific (or desktop-specific) code here
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
