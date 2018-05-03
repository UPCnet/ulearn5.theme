$(document).ready(function () {
  // $("#sso").click(function (data) {
  //   var u = $("#__ac_name").val();
  //   var p = $("#__ac_password").val();
  //   // debugger;
  //   $("#username").val(u);
  //   $("#password").val(p);
  //   $("#submit").trigger('click');
  //   // $.post("http://pc60012.estacions.upcnet.es/index.php/apps/loginviapost/login",
  //   //   {username: u, password: p})
  //   //   .done(function(aux) {
  //   //     alert(aux);
  //   //     alert( "second success" );
  //   //   })
  //   //   .fail(function() {
  //   //     alert( "error" );
  //   //   })
  // });
  $("#submit").click(function () {
    var u = $("#username").val();
    var p = $("#password").val();
    $("#__ac_name").val(u);
    $("#__ac_password").val(p);
    $('#sso').trigger('click');
  });
});
// Login a traves del form de abajo
// $("#submit").click(function () {
//   var u = $("#username").val();
//   var p = $("#password").val();
//   $("#__ac_name").val(u);
//   $("#__ac_password").val(p);
//   $('#sso').trigger('click');
// });
