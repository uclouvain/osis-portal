function my_startsWith(searchString, position){
    alert('my_startsWith');
    //Necessary because IE 11 does not support startsWith with strings.
    position = position || 0;
    return this.substr(position, searchString.length) === searchString;
}

if (!String.prototype.startsWith) {
    String.prototype.startsWith = function(searchString, position){
        position = position || 0;
        return this.substr(position, searchString.length) === searchString;
    };
}