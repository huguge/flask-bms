$(document).ready(function(){
    var search_btn =  $('#search-btn')
    if(search_btn.length>0){
        search_btn.on('click',function(e){
            e.preventDefault();
            var search_term = $('#search-term').val()
            if(search_term.length>0 && search_term.length<100){
                window.location.replace(window.location.href+'?search='+search_term)
            }else{
                console.log('Search length is not enough or too long')
            }
        })
    }
});