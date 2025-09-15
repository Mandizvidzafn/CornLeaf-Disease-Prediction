$(document).ready(function () {
    // Init
    $('.image-section').hide();
    $('.loader').hide();
    $('#result').hide();
    function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $('#imagePreview').attr( 'src', e.target.result );
            }
            reader.readAsDataURL(input.files[0]);
        }
    }
    $("#imageUpload").change(function () {
        $('.image-section').show();
        $('#btn-predict').show();
        $('#result').text('');
        $('#result').hide();
        readURL(this);
    });
    // Predict
    $('#btn-predict').click(function (e) {
        e.preventDefault();
        var form_data = new FormData($('#upload-file')[0]);

        // Show loading animation
        $(this).hide();
        $('.loader').show();
        $('#btn-try-another').show();

        // Make prediction by calling api /predict
        $.ajax({
            type: 'POST',
            url: '/predict',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            async: true,
            success: function (data) {
                // Get and display the result
                $('.loader').hide();

                // Update prediction + confidence
                $('#predictionResult').html(
                    `<h4 class="mb-0">Disease: <strong>${data.prediction}</strong></h4>
                     <p class="mb-0">Confidence: ${data.confidence}%</p>`
                );

                // Update recommendations block
                let recHtml = '<h5 class="mb-3">Recommendations</h5>';
                if (data.recommendations && data.recommendations.length > 0) {
                    recHtml += '<ul class="list-group text-start">';
                    data.recommendations.forEach(function (rec) {
                        recHtml += `<li class="list-group-item">${rec}</li>`;
                    });
                    recHtml += '</ul>';
                } else {
                    recHtml += '<p>No specific recommendations available.</p>';
                }
                $('.card.shadow.p-4').html(recHtml);

                // Show result smoothly
                $('#result').fadeIn(600);
                console.log('Success!');
            },
        });
    });

});
