<?php
// Read-only bounded receipt for the reference synthetic package.
define('CLI_SCRIPT', true);
require('/var/www/moodle/config.php');
$key = 'nikway:74f529fe-c81d-4d0c-98c8-56c31cfdd001:1.0.0';
$courses = $DB->get_records('course', ['idnumber' => $key]);
$out = ['course_count' => count($courses), 'courses' => []];
foreach ($courses as $course) {
    $assignments = $DB->get_records('assign', ['course' => $course->id]);
    $criteria = 0; $levels = 0;
    foreach ($assignments as $assignment) {
        $cm = get_coursemodule_from_instance('assign', $assignment->id);
        $area = $DB->get_record('grading_areas', ['contextid' => context_module::instance($cm->id)->id, 'component' => 'mod_assign', 'areaname' => 'submissions']);
        $definition = $DB->get_record('grading_definitions', ['areaid' => $area->id, 'method' => 'rubric']);
        foreach ($DB->get_records('gradingform_rubric_criteria', ['definitionid' => $definition->id]) as $criterion) {
            $criteria++; $levels += $DB->count_records('gradingform_rubric_levels', ['criterionid' => $criterion->id]);
        }
    }
    $out['courses'][] = ['id' => (int)$course->id, 'pages' => $DB->count_records('page', ['course' => $course->id]),
        'assignments' => count($assignments), 'rubric_criteria' => $criteria, 'rubric_levels' => $levels,
        'enrolments' => $DB->count_records_sql('SELECT COUNT(*) FROM {user_enrolments} ue JOIN {enrol} e ON e.id=ue.enrolid WHERE e.courseid=?', [$course->id])];
}
echo json_encode($out) . "\n";
