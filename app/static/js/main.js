// getParameterByName will get the query string from url
function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}
function setParameterByName(key,value,url){
    var querySplit = url.split('?')
    if(querySplit.length==1){
        return url+'?'+key+'='+value
    }
    if(getParameterByName('search',location.href)===null){
      return url+'&'+key+'='+value
    }
    var new_query = querySplit[1].split('&').map(function(q){
        if(q.startsWith('search')){
            return 'search='+value
        }else{
            return q
        }
    }).join('&')
    return querySplit[0]+'?'+new_query
}
$(document).ready(function(){
    var search_btn =  $('#search-btn')
    if(search_btn.length>0){
        search_btn.on('click',function(e){
            e.preventDefault();
            var search_term = $('#search-term').val()
            if(search_term.length>0 && search_term.length<50){

                location.replace(setParameterByName('search',search_term,location.href))
            }else{
                location.replace(setParameterByName('search','',location.href))
                // toastr.error('搜索内容长度不符合要求')
            }
        })
    }
});