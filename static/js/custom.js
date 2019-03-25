jQuery(function ($){
	$('#addCapability').on('click', function(){
		var newCapability = $('#inputCapabilitiesAdd').val();
		if (newCapability.trim()) {
			var exists = false;
			$('#inputCapabilities option').each(function(){
				if (this.value.toUpperCase() == newCapability.toUpperCase()) {
					exists = true;
	        			return;
	    			}
			});

	    		if(exists){
	        		alert("Value Already Exists");
	    		}
			else{
				$('#inputCapabilities').append($('<option>', {value: newCapability, text: newCapability}));
			}
			$('#inputCapabilitiesAdd').val("");
		}
	});


	$('#removeCapability').on('click', function(){
		$("#inputCapabilities option:selected").remove();
	});

	$(document).ready(function(){
			var date_input=$('input[name="incidentDate"]');
			var container=$('container-fluid').length>0 ? $('container-fluid').parent() : "body";
			date_input.datepicker({
				format: 'mm/dd/yyyy',
				//startDate: new Date(),
				container: container,
				todayHighlight: true,
				autoclose: true
			})
	})
})

$(function() {
	$('#addResource').on('click', function() {
		var inputCapabilities = $('#inputCapabilities')[0].options;
		for (var i = 0; i < inputCapabilities.length; i++) {
			inputCapabilities[i].selected = true;
		}
	});
});

// Hide ESF that is selected as the Primary ESF in the Additional ESF field
$(function(){
	$('#inputPrimaryESF').on('change', function() {

		//Display all Additional ESFs
		$('#inputSecondaryESFs option').show();
		//Select current value of primary ESF
		var selectedPrimaryESF = $('#inputPrimaryESF option:selected').val();

		//Deselect as Additional ESF if it is selected as Primary ESF
		$('#inputSecondaryESFs option[value="'+selectedPrimaryESF+'"]').prop("selected", false);

		//Hide Primary ESF from list Additional ESF list
		$('#inputSecondaryESFs option[value="'+selectedPrimaryESF+'"]').hide();
	});
});

// If want to select Additional ESFs without CTRL + CLICK, but interaction changes a bit.
// Also allows deselection of Additional ESFs. Otherwise would need to cancel out of form.

// $(function(){
// 	$('#inputSecondaryESFs option').mousedown(function (e){
// 		console.log("Entered")
// 		e.preventDefault();
// 		$(this).toggleClass('selected');
// 		$(this).prop('selected', !$(this).prop('selected'));
// 		return false;
// 	});
// });

// Add decimals to Longitude/Latitude/Cost
$(function() {
	// Writing a function did not work, so had to repeat
	// Convert longitude intput to 3 decimals
	$('#inputLon').on('change', function(){
		var value = $('#inputLon').val();
		if(isNaN(value) || value == "" || value == null){
			var decConv = (0).toFixed(6);
		} else{
			var decConv = (parseFloat(value) || 0).toFixed(6);
		}
		$('#inputLon').val(decConv);
	});

	// Convert latitude intput to 3 decimals
	$('#inputLat').on('change', function(){
		var value = $('#inputLat').val();
		if(isNaN(value) || value == "" || value == null){
			var decConv = (0).toFixed(6);
		} else{
			var decConv = (parseFloat(value) || 0).toFixed(6);
		}
		$('#inputLat').val(decConv);
	});

	// Convert cost intput to 2 decimals
	$('#inputCost').on('change', function(){
		var value = $('#inputCost').val();
		if(isNaN(value) || value == "" || value == null){
			var decConv = (0).toFixed(2);
		} else{
			var decConv = (parseFloat(value) || 0).toFixed(2);
		}
		$('#inputCost').val(decConv);
	});

	// Convert max distance to 2 decimals
	$('#inputMaxDistance').on('change', function(){
		var value = $('#inputMaxDistance').val();
		if(isNaN(value) || value == "" || value == null){
			var decConv = (0).toFixed(2);
		} else{
			var decConv = (parseFloat(value) || 0).toFixed(2);
		}
		$('#inputMaxDistance').val(decConv);
	});
});

// Start of JQuery-Validate forms
$(function() {

	// Add Resource
	$('#resourceForm').validate({
		// Define error class in CSS
		errorClass: "my-error-class",

		// Write rules for field validation
		rules: {
			inputResourceName: {
				required: true,
				maxlength: 100
			},
			inputPrimaryESF: {
				required: true
			},
			inputLon: {
				required: true,
				number: true,
				range: [-180, 180]
			},
			inputLat: {
				required: true,
				number: true,
				range: [-90, 90]
			},
			inputCost: {
				required: true,
				number: true,
				range: [0, 99999999.99]
			},
			inputPer: {
				required: true
			},
			intputModel: {
				maxlength: 250
			},
			inputMaxDistance: {
				number: true,
				range: [0, 25000]
			},
			inputCapabilities: {
			},
			inputCapabilitiesAdd: {
				maxlength: 100
			}
		},

		// Write customized messages
		messages: {
			inputLon: {
				range: "Longitude is between -180 and 180"
			},
			inputLat: {
				range: "Latitude is between -90 and 90"
			},
			inputCost: {
				range: "Cost is between 0 and 99,999,999.99"
			},
			inputMaxDistance: {
				number: "Please enter a number",
				range: "Distance is between 0 and 25000"
			},
		}
	});

	// Add Incident
	$('#incidentForm').validate({

		errorClass: "my-error-class",

		rules: {
			inputDeclaration: {
				required: true
			},
			incidentDate: {
				required: true
			},
			inputDescription: {
				required: true,
				maxlength: 100
			},
			inputLon: {
				required: true,
				number: true,
				range: [-180, 180]
			},
			inputLat: {
				required: true,
				number: true,
				range: [-90, 90]
			}
		},

		messages: {
			inputLon: {
				range: "Longitude is between -180 and 180"
			},
			inputLat: {
				range: "Latitude is between -90 and 90"
			}
		}
	});


	// Search for Resources
	$('#searchForm').validate({
		errorClass: "my-error-class",

		rules: {
			inputKeyword: {
				maxlength: 100
			},
			inputLocation: {
				required: function(element){
					return $('#inputIncident').val()!="";
				},
				digits: true,
				range: [0, 25000]
			},
			inputIncident: {
				required: function(element){
					return $('#inputLocation').val()!="";
					}
				}
		},

		messages: {
			inputLocation: {
				digits: "Enter integer between 0 and 25,000",
				range: "Enter integer between 0 and 25,000",
				required: "Please enter a distance for the incident"
			},
			inputIncident: {
				required: "Please enter an incident for the distance"
			}
		}
	});
});
