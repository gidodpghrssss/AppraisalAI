/**
 * Apeko Website JavaScript
 */

// Track page views
function trackPageView(page) {
    const sessionId = localStorage.getItem('apeko_session_id') || generateSessionId();
    
    // Store session ID
    if (!localStorage.getItem('apeko_session_id')) {
        localStorage.setItem('apeko_session_id', sessionId);
    }
    
    // Track page view
    fetch('/api/v1/website/track', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            page: page,
            session_id: sessionId,
            time_spent: 0
        })
    }).catch(error => console.error('Error tracking page view:', error));
    
    // Start timer for time spent
    window.pageLoadTime = new Date();
    
    // Track time spent when leaving page
    window.addEventListener('beforeunload', function() {
        const timeSpent = Math.round((new Date() - window.pageLoadTime) / 1000);
        
        // Use sendBeacon for more reliable tracking on page exit
        navigator.sendBeacon('/api/v1/website/track', JSON.stringify({
            page: page,
            session_id: sessionId,
            time_spent: timeSpent
        }));
    });
}

// Generate a random session ID
function generateSessionId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// Smooth scroll for navigation links
document.addEventListener('DOMContentLoaded', function() {
    // Track page view
    const currentPage = window.location.pathname.replace(/^\//, '').replace(/\/$/, '') || 'home';
    trackPageView(currentPage);
    
    // Smooth scroll for navigation links
    const navLinks = document.querySelectorAll('a[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Mobile menu toggle
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');
    
    if (menuToggle && mobileMenu) {
        menuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('active');
            this.classList.toggle('active');
        });
    }
    
    // Contact form validation
    const contactForm = document.getElementById('contact-form');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Basic validation
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const service = document.getElementById('service').value;
            const message = document.getElementById('message').value;
            
            if (!name || !email || !service || !message) {
                alert('Please fill in all required fields.');
                return;
            }
            
            // Email validation
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                alert('Please enter a valid email address.');
                return;
            }
            
            // Submit form
            const formData = new FormData(contactForm);
            
            fetch('/api/v1/website/contact', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    const successMessage = document.createElement('div');
                    successMessage.className = 'alert alert-success';
                    successMessage.textContent = data.message;
                    
                    contactForm.reset();
                    contactForm.parentNode.insertBefore(successMessage, contactForm);
                    
                    // Remove success message after 5 seconds
                    setTimeout(() => {
                        successMessage.remove();
                    }, 5000);
                } else {
                    alert('Error submitting form: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error submitting form:', error);
                alert('Error submitting form. Please try again later.');
            });
        });
    }
    
    // Newsletter subscription
    const newsletterForm = document.getElementById('newsletter-form');
    
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Basic validation
            const email = document.getElementById('newsletter-email').value;
            
            if (!email) {
                alert('Please enter your email address.');
                return;
            }
            
            // Email validation
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                alert('Please enter a valid email address.');
                return;
            }
            
            // Submit form
            const formData = new FormData(newsletterForm);
            
            fetch('/api/v1/website/subscribe', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    const successMessage = document.createElement('div');
                    successMessage.className = 'alert alert-success';
                    successMessage.textContent = data.message;
                    
                    newsletterForm.reset();
                    newsletterForm.parentNode.insertBefore(successMessage, newsletterForm);
                    
                    // Remove success message after 5 seconds
                    setTimeout(() => {
                        successMessage.remove();
                    }, 5000);
                } else {
                    alert('Error subscribing: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error subscribing:', error);
                alert('Error subscribing. Please try again later.');
            });
        });
    }
});
