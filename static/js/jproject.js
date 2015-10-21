$(document).ready(function() {
	$(".btndelete").click(function(event){
	  event.preventDefault();
	  //~ console.log("este es");
	  // console.log(this.id);
	});
	
	$("#btncreateproject").click(function(){
		// alert ($('#fraseB').val() != "")
		if($('#fraseB').val() != ""){
		 $('#load').show(); //lateral div
		 $("#msj").append("<p class='text-primary'><span class='fa  fa-send fa-fw'></span>Enviando los datos del formulario<br/>");
		 $("#id_nombre").focus();
		 var timer;
		 $.ajax({
			url : "/gestionproyectos/nuevoProyecto/", // the endpoint
			type : "POST", // http method
			data : $("#formproject").serialize(), 
			beforeSend: function(){
				var mess=""
				timer= setInterval(function() { //bucle para consultar el estado del proceso
					console.log("ajax pide ");
					$.ajax({
						url : "logmensajes/", //the endpoint 
						type : "GET", //http method
						success : function(json) {
							console.log("llega:" +json['mensaje']);
							// $("#loadgif").show();
							if(json['mensaje'].indexOf("STOP") == -1){  //parada de emergencia
								if(json['mensaje'].indexOf("EOF") != -1){ //si ya termino el proceso no pido mas
									$("#msj").append(json['mensaje'].replace("EOF","..."));
									clearInterval(timer);
								}else{
									console.log("mess >> "+mess+"!= "+ json['mensaje'])
									if(mess != json['mensaje']){  //si no ha terminado agrege al visualizador
										console.log("mess >> "+mess)
										$("#msj").append(json['mensaje'].replace(mess," "));
										mess=json['mensaje'];
									}else{ $("#msj").append("."); }//agrega puntos cada vez que no hay cambios
								}
							}else{
								strproblem= json['mensaje'].replace(mess," ");
								$("#msj").append(strproblem.slice(0,strproblem.indexOf("STOP")));
								$("#divproceso").removeClass('panel-success').addClass('panel-danger')
								$("#msj").append("<span class='fa fa-times fa-fw'></span>"+"El servidor envio señal de parada"+"<br/>");								
								console.log(json['mensaje']);
								clearInterval(timer);
							}
						},
						error : function(xhr,errmsg,err) {
							console.log(err);
							clearInterval(timer);
						}
					});	
				}, 5000);
			},
			success : function(json) {
				// $("#msj").append("<p class='text-success'><span class='fa  fa-check fa-fw'></span>Se creo el proyecto,<b>"+$('#id_nombre').val()+"</p></b>");
				console.log("success "+json); // another sanity check
			},
			error : function(xhr,errmsg,err) {
				console.log(errmsg,err); 
				$("#divproceso").removeClass('panel-success').addClass('panel-danger')
				$("#msj").append("<span class='fa fa-times fa-fw'></span>"+"Opps! Hubo problemas, lo sentimos"+"<br/>");
				clearInterval(timer);
				// $("#sincampos").html("<center>Problema de creacion</center>");				
				// $("#sincampos").show();				
			}
		});
		}else{
			$("#sincampos").html("<center>Para continuar debes llenar los campos</center>");
			$("#sincampos").show();
			$("#id_nombre").focus();
		}
	});
});

