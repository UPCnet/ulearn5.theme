  $(document).ready(function (event) {
      intervalflash = setInterval(function (event) {
          $('.ulearnboxflash .carousel').carousel('cycle')
          clearInterval(intervalflash)
          console.log('intervalflash')
      }, 2000)

  })
