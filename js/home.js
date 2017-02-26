$(document).ready(function() {
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
    var ev = $("#events table");
    for(var i in events) {
      ev.append(
      '<tr class="' + (i % 2 == 0 ? 'entry' : '') + '">\
         <td class="evname"></td>\
         <td class="evdate"></td>\
         <td class="evloc"></td>\
       </tr>');
    }
    $("#events .evname").text(function(i) { return events[i].name; });
    $("#events .evdate").text(function(i) { return events[i].date.slice(0, -9); });
    $("#events .evloc").text(function(i) { return events[i].where; });
  }
  //end events
  //TIMER STUFF
  function setCountdown(to) {
    var endDate = new Date(to.date).getTime();
    $("#countdown-desc").text(to.name);
    //Do it once so it doesn't start empty
    setCountdownTimer(endDate);
    var resetTime = setInterval(function(){
      setCountdownTimer(endDate);
    }, 1000); //Every second
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
  }
  //end timer stuff
});
