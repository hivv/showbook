


function book(){
	var catChosen=$('#catChoose').val();
	var nbPlaces=$('#nbpl').val();
	var social=$('#soc').val();	  
	document.getElementById("result").innerHTML = 'Booking... Please Wait...';	  
	  $.ajax({
		type:"POST",
		url: "/book",        
		dataType: "json",
		contentType: "application/json; charset=utf-8",
		data: JSON.stringify({
			Pseudo: pseudo,
			Show: name,
			nbPlaces:nbPlaces,
			cat:catChosen, 
			social:social
		}),
		success: function(data){
			document.getElementById("result").innerHTML = data['result'];
			if (data['success']) { 
				console.log(data['token']);
				// Check browser support
				if (typeof(Storage) != "undefined") {
					// Store
						localStorage.setItem("token", data['token']);
					//document.location.href="logged.html" ;
					// Retrieve
					//document.getElementById("result").innerHTML = localStorage.getItem("lastname");
				} else {
					document.getElementById("result").innerHTML = "Sorry, your browser does not support Web Storage...";
				}
				//document.location.href="logged.html" ;
			}
			else {
				document.getElementById("result").innerHTML = data['result'];
			}	
		},
		error:function(){
			alert("une erreur est survenue");
		},
		default: function(){
			alert("défaut");
		}             
	});
} 


