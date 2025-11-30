$(document).ready(function() {
    console.log("JavaScript is running!");  // Log message to confirm JS is running

    // Fetch courses and teachers using AJAX
    $.get("/manage/get_courses_and_teachers", function(data) {
        console.log("Data fetched:", data);  // Log the data to ensure it's being received

        // Populate courses dropdown
        if (data.courses && data.courses.length > 0) {
            data.courses.forEach(function(course) {
                $('#course_id').append(new Option(course.name, course.id));
            });
        } else {
            console.log("No courses found.");
        }

        // Populate teachers dropdown
        if (data.teachers && data.teachers.length > 0) {
            data.teachers.forEach(function(teacher) {
                $('#teacher_id').append(new Option(teacher.name, teacher.id));
            });
        } else {
            console.log("No teachers found.");
        }
    }).fail(function(xhr, status, error) {
        console.error("Error fetching data:", status, error);
        alert("An error occurred while fetching the data for courses and teachers.");
    });
});
