document.addEventListener("DOMContentLoaded", function () {
  // Get the button and form
  const showFilterForm = document.getElementById("showFilterForm");
  const formContainerFilter = document.getElementById("formContainerFilter");

  // Add event listener to button
  showFilterForm.addEventListener("click", function () {
    // Toggle form visibility (show/hide)
    if (formContainerFilter.style.display === "none") {
      formContainerFilter.style.display = "block"; // Show the form
    } else {
      formContainerFilter.style.display = "none"; // Hide the form
    }
  });
});
