$('.confirmation').on('click', function () {
        var choice = confirm('Are you sure want to delete this post?');
        if(choice == true){
          return "{{  }}"
        }
        else {
          return alert('Post deletion was cancelled.');
        }
    });
