document.addEventListener('DOMContentLoaded', function() {
    const menuIcon = document.querySelector('.menu-icon');
    const navLinks = document.querySelector('.nav-links');
  
    if (menuIcon) { // Check if menuIcon exists
        menuIcon.addEventListener('click', function() {
            navLinks.classList.toggle('active'); // Toggle the 'active' class on the nav links
        });
    }
});


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
  

  window.addEventListener('scroll', () => {
    const scrollToTopBtn = document.getElementById('scrollToTopBtn');
    if (window.scrollY > 100) {
        scrollToTopBtn.style.display = 'block';
    } else {
        scrollToTopBtn.style.display = 'none';
    }
});

function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

document.getElementById('scrollToTopBtn').addEventListener('click', scrollToTop);