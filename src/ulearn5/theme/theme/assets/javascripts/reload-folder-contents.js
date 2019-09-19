$(document).ready(function(){
    $("table .fc-breadcrumbs-container a").on("click", function(){
        var url_redirect = $("body").attr("data-portal-url");
        if($(this).attr("data-path") != "/"){
             url_redirect += "/" + $(this).attr("data-path")
        }
        $(location).attr("href", url_redirect + "/folder_contents");
    });

    $("table tr.itemRow.folder a").on("click", function(){
        $(location).attr("href", $(this).attr("href") + "/folder_contents");
    });
});
