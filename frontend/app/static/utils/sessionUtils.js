export function getCookie(name) {
    const value = `; ${document.cookie}`; // Add a semicolon for easier parsing
    console.log("Document Cookies:", document.cookie); // Log all cookies for debugging
    const parts = value.split(`; ${name}=`); // Split based on the cookie name

    if (parts.length === 2) {
        const cookieValue = parts.pop().split(';').shift(); // Get the cookie value
        console.log(`Cookie "${name}" found:`, cookieValue); // Log the found cookie
        return cookieValue; // Return the cookie value
    }
    
    console.log(`Cookie "${name}" not found.`); // Log if cookie is not found
    return null; // Return null if cookie does not exist
}
