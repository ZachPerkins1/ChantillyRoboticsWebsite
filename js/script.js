$(document).ready(function(){
  if($("#about-first").length!=0){ //So it only runs on the one page
    $(".subtitle").click(function(){
      $(this).next().slideToggle(300); //Goes inside the contentbox, finds all p's, get's the second (index 1)
    });
  }
});
