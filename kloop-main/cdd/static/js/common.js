document.addEventListener('DOMContentLoaded', function() {
    const menuIcon = document.querySelector('.menu-icon');
    const navLinks = document.querySelector('.nav-links');
  
    menuIcon.addEventListener('click', function() {
        navLinks.classList.toggle('active');
    });
  });
  
  let slideIndex = 0;
  showSlide(slideIndex);
  
  function showSlide(n) {
      const slides = document.querySelectorAll('.carousel img');
      const dots = document.querySelectorAll('.dot');
  
      // Hide all slides and remove active class from dots
      slides.forEach(slide => slide.style.display = "none");
      dots.forEach(dot => dot.classList.remove("active"));
  
      // Adjust slide index to ensure it stays within bounds
      slideIndex = (n + slides.length) % slides.length;
  
      // Show current slide and set corresponding dot as active
      slides[slideIndex].style.display = "block";
      dots[slideIndex].classList.add("active");
  }
  
  // Event listener for previous button
  document.getElementById("prev").addEventListener("click", function() {
      showSlide(slideIndex - 1);
  });
  
  // Event listener for next button
  document.getElementById("next").addEventListener("click", function() {
      showSlide(slideIndex + 1);
  });
  
  // Automatic slide change every 3 seconds
  setInterval(function() {
      showSlide(slideIndex + 1);
  }, 3000);
  
  
  // Function to start counting animation
  function startCountingAnimation(targetElement) {
      const startNumber = 1; // Start counting from 1
      const endNumber = 100;
      const duration = 4000; // Animation duration in milliseconds
      const steps = endNumber - startNumber; // Total steps from start to end
      const interval = duration / steps; // Interval for each step
    
      let currentNumber = startNumber;
      const increment = 1; // Increment by 1 for each step
    
      const intervalId = setInterval(() => {
        if (currentNumber <= endNumber) {
          // Update the displayed number
          targetElement.textContent = currentNumber;
          currentNumber += increment;
        } else {
          // Display "100+" when the count reaches 100
          targetElement.textContent = "100+";
          // Stop the interval when reaching the end number
          clearInterval(intervalId);
        }
      }, interval);
    }
    
    // Function to observe element intersection
    function CountingAnimation(countingRef, startCountingAnimation) {
      const options = {
        root: null,
        rootMargin: '0px',
        threshold: 0.5 // Trigger when 50% of the target element is visible
      };
    
      const callback = (entries, observer) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            startCountingAnimation(entry.target);
            observer.unobserve(entry.target);
          }
        });
      };
    
      const observer = new IntersectionObserver(callback, options);
      if (countingRef) {
        observer.observe(countingRef);
      }
    
      return () => {
        if (countingRef) {
          observer.unobserve(countingRef);
        }
      };
    }
    
    // Get references to the counting containers
    const countingRefCr3 = document.getElementById("countingCr3");
    const countingRefCr6 = document.getElementById("countingCr6");
    
    // Start counting animation for cr3
    CountingAnimation(countingRefCr3, startCountingAnimation);
    // Start counting animation for cr6
    CountingAnimation(countingRefCr6, startCountingAnimation);
    
  
    // When the page is scrolled, check if the scroll position is greater than 100 pixels
  // Smooth scroll to the top when the arrow is clicked
  $('.arrow a').click(function() {
    $('html, body').animate({
      scrollTop: 0
    }, 500); // Adjust the duration (in milliseconds) here for faster scrolling
    return false;
  });
  /* */
  
  
  /*socialmedia */
  document.addEventListener('DOMContentLoaded', function() {
    const socialIcons = document.querySelectorAll('.social-icon');
    
    socialIcons.forEach(icon => {
      icon.addEventListener('click', function(event) {
        event.preventDefault();
        const socialName = icon.getAttribute('data-social');
        const socialUrl = getSocialUrl(socialName);
        window.open(socialUrl, '_blank');
      });
    });
    
    function getSocialUrl(socialName) {
      // Define your social media URLs
      const socialUrls = {
        'Telegram': 'https://telegram.org/',
        'Instagram': 'https://www.instagram.com/',
        'Facebook': 'https://www.facebook.com/profile.php?id=61559804274395',
        'Twitter': 'https://twitter.com/',
        'LinkedIn': 'https://www.linkedin.com/',
        'YouTube': 'https://www.youtube.com/',
        'TikTok': 'https://www.tiktok.com/@amco_interiorfurniture?_t=8mXEfzKb4HV&_r=1'
      };
      return socialUrls[socialName];
    }
  });
  
  
  
  
      function sendEmail() {
          // Get form data
          const name = document.getElementById('name').value;
          const email = document.getElementById('email').value;
          const phone = document.getElementById('phone').value;
          const message = document.getElementById('message').value;
  
          // Send email using EmailJS
          emailjs.send("service_l4r6gkd", "template_ab6zjtk", {
              from_name: name,
              from_email: email,
              phone: phone,
              message: message
          })
          .then(function(response) {
              console.log("Email sent successfully", response);
              alert("Your message has been sent successfully!");
              // Optionally, clear the form fields
              document.getElementById('name').value = '';
              document.getElementById('email').value = '';
              document.getElementById('phone').value = '';
              document.getElementById('message').value = '';
          }, function(error) {
              console.error("Error sending email", error);
              alert("An error occurred while sending your message. Please try again later.");
          });
      }
      /* slider*/
      document.addEventListener('DOMContentLoaded', function() {
        const slides = document.querySelectorAll('.slider img');
        const navButtons = document.querySelectorAll('.slider-nav a');
        let currentSlide = 0;
        let intervalId;
    
        function showSlide(index) {
            slides.forEach((slide, i) => {
                if (i === index) {
                    slide.style.display = 'block';
                } else {
                    slide.style.display = 'none';
                }
            });
        }
    
        function nextSlide() {
            currentSlide = (currentSlide + 1) % slides.length;
            showSlide(currentSlide);
        }
    
        function prevSlide() {
            currentSlide = (currentSlide - 1 + slides.length) % slides.length;
            showSlide(currentSlide);
        }
    
        function startAutoPlay() {
            intervalId = setInterval(nextSlide, 3000);
        }
    
        function stopAutoPlay() {
            clearInterval(intervalId);
        }
    
        // Add event listeners to navigation buttons
        navButtons.forEach((button, index) => {
            button.addEventListener('click', function(event) {
                event.preventDefault();
                stopAutoPlay();
                currentSlide = index;
                showSlide(currentSlide);
                startAutoPlay();
            });
        });
    
        // Start auto-play
        startAutoPlay();
    });
    
  /* hoMEjs*/
  const myslide = document.querySelectorAll('.myslide'),
        dot = document.querySelectorAll('.dot');
  let counter = 1;
  slidefun(counter);
  
  let timer = setInterval(autoSlide, 8000);
  function autoSlide() {
      counter += 1;
      slidefun(counter);
  }
  function plusSlides(n) {
      counter += n;
      slidefun(counter);
      resetTimer();
  }
  function currentSlide(n) {
      counter = n;
      slidefun(counter);
      resetTimer();
  }
  function resetTimer() {
      clearInterval(timer);
      timer = setInterval(autoSlide, 8000);
  }
  
  function slidefun(n) {
      
      let i;
      for(i = 0;i<myslide.length;i++){
          myslide[i].style.display = "none";
      }
      for(i = 0;i<dot.length;i++) {
          dot[i].className = dot[i].className.replace(' active', '');
      }
      if(n > myslide.length){
         counter = 1;
         }
      if(n < 1){
         counter = myslide.length;
         }
      myslide[counter - 1].style.display = "block";
      dot[counter - 1].className += " active";
  }
  /*email */
  
  emailjs.init('D3VuuvmzMea1ZpQ3l');
  
    // Event listener for form submission
    document.getElementById('submit-btn').addEventListener('click', function() {
      sendEmail();
    });
  
  function sendEmail() {
    // Get form data
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;
    const message = document.getElementById('message').value;
  
    // Send email using EmailJS
    emailjs.send("service_l4r6gkd", "template_ab6zjtk", {
      from_name: name,
      from_email: email,
      phone: phone,
      message: message
    })
    .then(function(response) {
      console.log("Email sent successfully", response);
      // Show success message
      showAlert("Your message has been sent successfully!");
      // Optionally, clear the form fields
      clearFormFields();
  }, function(error) {
      console.error("Error sending email", error);
      // Show error message
      showAlert("An error occurred while sending your message. Please try again later.", true);
  });
  }
  
  function showAlert(message, isError = false) {
  alert(message); // Simple alert popup
  // You can customize this to use a styled modal dialog for a better user experience
  }
  
  function clearFormFields() {
  // Clear form fields
  document.getElementById('name').value = '';
  document.getElementById('email').value = '';
  document.getElementById('phone').value = '';
  document.getElementById('message').value = '';
  }
  
  document.addEventListener('DOMContentLoaded', function() {
    const lines = document.querySelectorAll('.for-decades-amco .line');
  
    // Function to trigger auto-write animation for each line
    function autoWriteLine(line) {
      // Start animation
      line.style.animation = 'autoWrite 1s steps(40) forwards';
      // Add event listener for animation end
      line.addEventListener('animationend', function() {
        // Ensure line remains visible after animation
        line.style.opacity = '1';
        // Hide the border line
        line.classList.add('hide-border');
        // Show the next line if available
        const nextLineIndex = Array.from(lines).indexOf(this) + 1;
        if (nextLineIndex < lines.length) {
          autoWriteLine(lines[nextLineIndex]);
        }
      });
    }
  
    // Trigger the animation sequence for the first line
    autoWriteLine(lines[0]);
  });
  
  
  
  document.addEventListener('DOMContentLoaded', (event) => {
    let items = document.querySelectorAll('.carousel-container .carousel-list .carousel-item');
    let container = document.querySelector('.carousel-container');
    let dots = document.querySelectorAll('.carousel-dots li');
    let nextBtn = document.querySelector('.carousel-arrows .next');
    let prevBtn = document.querySelector('.carousel-arrows .prev');
  
    let lastIndex = items.length - 1;
    let activeIndex = 0;
    let zIndex = 2;
  
    nextBtn.onclick = () => {
        let newIndex = activeIndex + 1 > lastIndex ? 0 : activeIndex + 1;
        setActiveItem(newIndex);
    };
  
    prevBtn.onclick = () => {
        let newIndex = activeIndex - 1 < 0 ? lastIndex : activeIndex - 1;
        setActiveItem(newIndex);
    };
  
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            setActiveItem(index);
        });
    });
  
    const setActiveItem = (newIndex) => {
        if (newIndex === activeIndex) return;
        activeIndex = newIndex;
        showSlider();
    };
  
    const showSlider = () => {
        container.style.pointerEvents = 'none';
        let activeItem = document.querySelector('.carousel-container .carousel-list .carousel-item.active');
        if (activeItem) activeItem.classList.remove('active');
        zIndex++;
        items[activeIndex].style.zIndex = zIndex;
        items[activeIndex].classList.add('active');
  
        container.classList.add('effect');
  
        let activeDot = document.querySelector('.carousel-dots li.active');
        if (activeDot) activeDot.classList.remove('active');
        dots[activeIndex].classList.add('active');
  
        clearTimeout(removeEffect);
        removeEffect = setTimeout(() => {
            container.classList.remove('effect');
            container.style.pointerEvents = 'auto';
        }, 1500);
  
        clearTimeout(autoRun);
        autoRun = setTimeout(() => {
            nextBtn.click();
        }, 5000);
    };
  
    let removeEffect;
    let autoRun = setTimeout(() => {
        nextBtn.click();
    }, 5000);
  });