<?php
// Operator-only CLI. Input must come from content-import.py after strict package admission.
define('CLI_SCRIPT', true);
require('/var/www/moodle/config.php');
require_once($CFG->dirroot . '/course/lib.php');
require_once($CFG->dirroot . '/course/modlib.php');
require_once($CFG->dirroot . '/grade/grading/lib.php');
require_once($CFG->dirroot . '/grade/grading/form/rubric/lib.php');
require_once($CFG->libdir . '/enrollib.php');
\core\session\manager::set_user(get_admin());
$input = json_decode(stream_get_contents(STDIN), true, 30, JSON_THROW_ON_ERROR);
// Validate all requested subjects before locking or mutating any course state.
$allowedsubjects = [
    'learners' => '00000000-0000-4000-8000-000000000001',
    'reviewers' => '00000000-0000-4000-8000-000000000003',
];
foreach ($allowedsubjects as $group => $allowed) {
    if (!isset($input[$group]) || !is_array($input[$group])) {
        throw new RuntimeException('Explicit enrolment arrays required');
    }
    foreach ($input[$group] as $subject) {
        if ($subject !== $allowed) {
            throw new RuntimeException('Unauthorized synthetic subject for requested role');
        }
    }
}
$p = $input['package'];
$c = $p['course'];
$key = 'nikway:' . $p['packageId'] . ':' . $p['version'];
$marker = 'nikway-source-sha256:' . $input['raw_sha256'];
$lock = \core\lock\lock_config::get_lock_factory('nikway_content')->get_lock($key, 30);
if (!$lock) { throw new RuntimeException('Import lock unavailable'); }
try {
    $transaction = $DB->start_delegated_transaction();
    $course = $DB->get_record('course', ['idnumber' => $key]);
    if ($course && strpos($course->summary, $marker) === false) {
        throw new RuntimeException('Existing course identity has a different original package; refusing overwrite');
    }
    $created = !$course;
    function plain($text) { return '<div dir="auto">' . nl2br(s($text)) . '</div>'; }
    function module($type, $title, $section, $idnumber, $fields, $course) {
        global $DB;
        $data = (object) array_merge([
            'modulename' => $type, 'module' => $DB->get_field('modules', 'id', ['name' => $type], MUST_EXIST),
            'name' => $title, 'section' => $section, 'visible' => 1, 'cmidnumber' => $idnumber,
            'intro' => '', 'introformat' => FORMAT_HTML, 'showdescription' => 1,
        ], $fields);
        return add_moduleinfo($data, $course);
    }
    if ($created) {
        $categories = $DB->get_records('course_categories', [], 'sortorder ASC', 'id', 0, 1);
        $category = $categories ? reset($categories)->id : null;
        if (!$category) { throw new RuntimeException('Create a course category before importing'); }
        $course = create_course((object) [
            'category' => $category, 'fullname' => $c['title'],
            'shortname' => 'NK-' . $p['packageId'] . '-' . $p['version'],
            'idnumber' => $key, 'format' => 'topics', 'visible' => 1,
            'summary' => plain($c['description']) . '<!-- ' . s($marker) . ' -->',
            'summaryformat' => FORMAT_HTML, 'enablecompletion' => 1,
        ]);
        course_create_sections_if_missing($course, range(1, count($c['lessons']) + 1));
        $objectives = [];
        foreach ($c['objectives'] as $objective) { $objectives[$objective['id']] = $objective['description']; }
        foreach ($c['lessons'] as $lesson) {
            $body = plain($lesson['content']) . '<h3>اهداف یادگیری</h3>';
            foreach ($lesson['objectiveIds'] as $oid) { $body .= plain($objectives[$oid]); }
            $body .= '<h3>تمرین</h3>' . plain($lesson['practice']['prompt']) . plain($lesson['practice']['deliverable']);
            module('page', $lesson['title'], $lesson['position'], $lesson['id'], [
                'content' => $body, 'contentformat' => FORMAT_HTML, 'display' => 5,
                'printintro' => 0, 'printlastmodified' => 0, 'completion' => COMPLETION_TRACKING_MANUAL,
            ], $course);
        }
        $assessment = $c['assessment'];
        $maxscore = array_sum(array_column($c['rubric']['criteria'], 'maxScore'));
        $assignment = module('assign', 'ارزیابی انسانی — ' . $c['title'], count($c['lessons']) + 1,
            $c['id'] . ':assessment', [
                'intro' => plain($assessment['prompt']) . plain('حد متن راهنما: ' . $assessment['minCharacters'] . ' تا ' . $assessment['maxCharacters'] . ' نویسه. کنترل این حد به صورت خودکار در Moodle فعال نیست.'),
                'grade' => $maxscore, 'submissiondrafts' => 1, 'requiresubmissionstatement' => 0,
                'sendnotifications' => 0, 'sendlatenotifications' => 0, 'sendstudentnotifications' => 0,
                'duedate' => 0, 'cutoffdate' => 0, 'gradingduedate' => 0, 'allowsubmissionsfromdate' => 0,
                'teamsubmission' => 0, 'requireallteammemberssubmit' => 0, 'teamsubmissiongroupingid' => 0,
                'blindmarking' => 0, 'markingworkflow' => 0, 'markingallocation' => 0,
                'attemptreopenmethod' => 'manual', 'maxattempts' => -1,
                'assignsubmission_onlinetext_enabled' => 1, 'assignsubmission_file_enabled' => 0,
                'assignsubmission_onlinetext_wordlimitenabled' => 0,
                'assignfeedback_comments_enabled' => 1,
            ], $course);
        $manager = get_grading_manager(context_module::instance($assignment->coursemodule), 'mod_assign', 'submissions');
        $manager->set_active_method('rubric');
        $criteria = [];
        foreach ($c['rubric']['criteria'] as $i => $criterion) {
            $levels = [];
            foreach ($criterion['anchors'] as $j => $anchor) {
                $levels['NEWID' . $j] = ['score' => $anchor['score'], 'definition' => $anchor['description'], 'definitionformat' => FORMAT_PLAIN];
            }
            $criteria['NEWID' . $i] = ['sortorder' => $i, 'description' => $criterion['description'],
                                     'descriptionformat' => FORMAT_PLAIN, 'levels' => $levels];
        }
        $manager->get_controller('rubric')->update_definition((object) [
            'name' => $c['rubric']['id'] . ' v' . $c['rubric']['version'],
            'description_editor' => ['text' => 'Human review only. No Academy grade/status synchronization.', 'format' => FORMAT_PLAIN, 'itemid' => 0],
            'rubric' => ['criteria' => $criteria], 'status' => gradingform_controller::DEFINITION_STATUS_READY,
        ]);
    }
    $plugin = enrol_get_plugin('manual');
    $instances = enrol_get_instances($course->id, false);
    $manual = null;
    foreach ($instances as $instance) { if ($instance->enrol === 'manual') { $manual = $instance; break; } }
    if (!$manual) { $id = $plugin->add_instance($course); $manual = $DB->get_record('enrol', ['id' => $id], '*', MUST_EXIST); }
    foreach (['learners' => 'student', 'reviewers' => 'teacher'] as $group => $role) {
        $roleid = $DB->get_field('role', 'id', ['shortname' => $role], MUST_EXIST);
        foreach ($input[$group] as $username) {
            $user = $DB->get_record('user', ['username' => $username, 'deleted' => 0], '*', MUST_EXIST);
            $plugin->enrol_user($manual, $user->id, $roleid);
        }
    }
    rebuild_course_cache($course->id, true);
    $transaction->allow_commit();
    echo json_encode(['status' => $created ? 'created' : 'existing', 'course_id' => (int)$course->id,
        'course_url' => $CFG->wwwroot . '/course/view.php?id=' . $course->id,
        'package_id' => $p['packageId'], 'source_sha256' => $input['raw_sha256'],
        'native_rubric' => true, 'automatic_character_limit' => false, 'academy_status_sync' => false], JSON_UNESCAPED_UNICODE) . "\n";
} finally { $lock->release(); }
