$( document ).ready(function(){
  var tag = document.createElement('script');
  tag.src = "https://www.youtube.com/iframe_api";
  var firstScriptTag = document.getElementsByTagName('script')[0];
  firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

  var player = new Array();

  setTimeout(function(){
    loadYTVideos();
  }, 1500);

  function loadYTVideos(){
    $('.player').each(function( index ) {
      var idYT = $(this).attr("data-YT");
      function onYouTubeIframeAPIReady() {
        player[idYT] = new YT.Player('player-'+idYT, {
          videoId: idYT,
        });
      }
      try {
        onYouTubeIframeAPIReady();
      }catch(err){
         console.log('%c' + err, 'color: #ff0000');
        $("#player-"+idYT).html("\
          <div class='errorYT'>\
            <p>Error loading Youtube</p>\
            <button onclick='loadYTVideos()'>Click to reload</button>\
          </div>\
        ");
      }
    });
  }

  function pause(){
    var youtubeActive = $('.carousel-video-yt.active iframe');
    var videoActive = $('.carousel-video.active video')[0];
    if(youtubeActive[0]){
      var idYT = youtubeActive.attr("data-yt");
      player[idYT].pauseVideo();
    }

    if(videoActive){
      videoActive.pause();
    }
  }
});
