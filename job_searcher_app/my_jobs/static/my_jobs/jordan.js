
$(function() {
    const para = document.querySelectorAll('td.dateNotExpired');
    console.log(para);
    para.forEach(ChangeDate);



    function ConvertMon(letters){
        if (letters === 'Jan'){
            return '0';
        }else if(letters === 'Feb'){
            return '1';
        }else if(letters === 'Mar'){
            return '2';
        }else if(letters === 'Apr'){
            return '3';
        }else if(letters === 'May'){
            return '4';
        }else if(letters === 'Jun'){
            return '5';
        }else if(letters === 'Jul'){
            return '6';
        }else if(letters === 'Aug'){
            return '7';
        }else if(letters === 'Sep'){
            return '8';
        }else if(letters === 'Oct'){
            return '9';
        }else if(letters === 'Nov'){
            return '10';
        }else if(letters === 'Dec'){
            return '11';
        }
    }

    function ChangeDate(item){
        var splitIt = item.innerText.split(' ');
        console.log(splitIt);
        var newDate = new Date(splitIt[2], ConvertMon(splitIt[0].slice(0,-1)), splitIt[1].slice(0,-1));
        console.log(newDate);
        var dateTester = IsDateOlder(newDate);
        if (dateTester === true){
           item.className = 'dateNotExpired';
        }
    }

    function IsDateOlder(date){
        var todaysDate = new Date();
        return todaysDate < date;
    
    
    }
    var todaysDate = new Date();




    







 });
 

 document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.fixed-action-btn');
    var instances = M.FloatingActionButton.init(elems, {
      direction: 'top'
    });
  });