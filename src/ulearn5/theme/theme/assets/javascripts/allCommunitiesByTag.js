var changeBlockHeight = function(){
    if($(document).width() >= 1185){
        $('.block:even').each(function(){
            block = $(this).find('.tagInfo');
            side = $(this).next().find('.tagInfo');
            blockHeight = $(block).height();
            sideHeight = $(side).height();
            if(sideHeight > blockHeight){
                block.height(sideHeight);
            }else{
                side.height(blockHeight);
            }
        });
    }else{
        $('.block .tagInfo').each(function(){
            $(this).height('auto');
        });
    }
}

changeBlockHeight();
$(window).resize(function(){
    changeBlockHeight();
});
