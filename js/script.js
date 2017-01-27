$(document).ready(function(){
  $(".contentbox").click(function(){
    $(this).find("p").eq(1).slideToggle(300); //Goes inside the contentbox, finds all p's, get's the second (index 1)
  });
});
