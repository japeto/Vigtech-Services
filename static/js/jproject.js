$(document).ready(function() {
	$(".btndelete").click(function(event){
	  event.preventDefault();
	  console.log("este es");
	  // console.log(this.id);
	  console.log("<<<<<este es>>>>>");
	});
	
	$("#btncreateproject").click(function(){
		// alert ($('#fraseB').val() != "")
		if($('#fraseB').val() != ""){
		 $('#load').show(); //lateral div
		 $("#msj").append("<p class='text-primary'><span class='fa  fa-send fa-fw'></span>Enviando los datos del formulario<br/>");
		 $("#id_nombre").focus();
		 $.ajax({
			url : "/gestionproyectos/nuevoProyecto/", // the endpoint
			type : "POST", // http method
			data : $("#formproject").serialize(), 
			success : function(json) {
				// alert(json)
				$("#msj").append("<p class='text-success'><span class='fa  fa-check fa-fw'></span>Se creo el proyecto,<b>"+$('#id_nombre').val()+"</p></b>");
				console.log("success "+json); // another sanity check
				$.ajax({
					url : "logmensajes/", // the endpoint 
					type : "GET", // http method
					success : function(json) {
						console.log("success "+json); // another sanity check
						console.log("llega:" +json['mensaje']);
						$("#loadgif").show();
						$("#msj").append(json['mensaje']);
					},
					error : function(xhr,errmsg,err) {
						console.log(err);
					}
				});	            
			},
			error : function(xhr,errmsg,err) {
				console.log(errmsg,err); 
				$("#divproceso").removeClass('panel-success').addClass('panel-danger')
				$("#msj").append("<label class='message-text'><span class='fa fa-times fa-fw'></span>"+"Opps! Hubo problemas, lo sentimos"+"</label><br/>");
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
		
		
		
		
		
		
		
		
    //~ $.ajax({
        //~ url : "gestionproyectos/nuevoProyecto/", // the endpoint
        //~ type : "POST", // http method
        //~ data : { 'fraseB' : $('#fraseB').val() }, 
        //~ success : function(result) {
		//~ }		
		//~ 
		
		
	
	//~ });
	//~ alert ($("#dprojectlist option:selected").text());

