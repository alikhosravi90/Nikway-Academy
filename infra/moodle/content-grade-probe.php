<?php
// Explicit synthetic integration fixture; never an educational/human assessment.
define('CLI_SCRIPT', true);
require('/var/www/moodle/config.php');
require('/tmp/nikway-content-binding.php');
require_once($CFG->dirroot . '/mod/assign/locallib.php');
if ($CFG->wwwroot !== 'http://localhost:18701') { throw new RuntimeException('Pilot only'); }
$course = $DB->get_record('course', ['idnumber' => 'nikway:74f529fe-c81d-4d0c-98c8-56c31cfdd001:1.0.0'], '*', MUST_EXIST);
$cm = get_coursemodule_from_id('assign', 25, $course->id, false, MUST_EXIST);
$context = context_module::instance($cm->id);
$users = [];
foreach (['learner' => '001', 'reviewer' => '003'] as $role => $suffix) {
    $sub = '00000000-0000-4000-8000-000000000' . $suffix;
    $user = $DB->get_record('user', ['username' => $sub, 'mnethostid' => $CFG->mnet_localhost_id], '*', MUST_EXIST);
    nikway_validate_content_binding($user, $sub, (int)$CFG->mnet_localhost_id);
    $users[$role] = $user;
}
if (has_capability('mod/assign:grade', $context, $users['learner']) ||
        !has_capability('mod/assign:grade', $context, $users['reviewer'])) {
    throw new RuntimeException('Role capability boundary failed');
}
\core\session\manager::set_user($users['reviewer']);
$assignment = new assign($context, $cm, $course);
$submission = $assignment->get_user_submission($users['learner']->id, false);
if (!$submission || $submission->status !== ASSIGN_SUBMISSION_STATUS_SUBMITTED) {
    throw new RuntimeException('Expected existing submitted synthetic learner work');
}
$existing = $assignment->get_user_grade($users['learner']->id, false);
if ($existing && $existing->grade >= 0) { throw new RuntimeException('Refuse overwriting existing grade'); }
$controller = get_grading_manager($context, 'mod_assign', 'submissions')->get_controller('rubric');
$definition = $controller->get_definition();
if (count($definition->rubric_criteria) !== 4) { throw new RuntimeException('Expected four rubric criteria'); }
$feedback = 'Synthetic integration test, not educational assessment';
$criteria = [];
foreach ($definition->rubric_criteria as $id => $criterion) {
    foreach ($criterion['levels'] as $levelid => $level) {
        if ((float)$level['score'] === 1.0) { $criteria[$id] = ['levelid' => $levelid, 'remark' => $feedback]; break; }
    }
}
if (count($criteria) !== 4) { throw new RuntimeException('Expected fixture score anchor in every criterion'); }
$tx = $DB->start_delegated_transaction();
$assignment->save_grade($users['learner']->id, (object)[
    'attemptnumber' => $submission->attemptnumber, 'addattempt' => 0, 'sendstudentnotifications' => 0,
    'advancedgrading' => ['criteria' => $criteria],
    'assignfeedbackcomments_editor' => ['text' => $feedback, 'format' => FORMAT_PLAIN],
]);
$grade = $assignment->get_user_grade($users['learner']->id, false);
$comment = $DB->get_record('assignfeedback_comments', ['grade' => $grade->id], '*', MUST_EXIST);
if ((float)$grade->grade !== 4.0 || $comment->commenttext !== $feedback || (int)$grade->grader !== (int)$users['reviewer']->id) {
    throw new RuntimeException('Persisted synthetic grade/feedback mismatch');
}
$tx->allow_commit();
echo json_encode(['status' => 'PASS_SYNTHETIC_CORE_API', 'course_id' => (int)$course->id, 'cm_id' => 25,
    'learner_cannot_grade' => true, 'reviewer_can_grade' => true, 'rubric_criteria_selected' => count($criteria),
    'synthetic_grade' => (float)$grade->grade, 'feedback' => $feedback, 'human_review_claim' => false,
    'learner_browser_feedback_verification' => 'pending']) . "\n";
