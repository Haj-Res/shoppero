$(document).on('click', function (e) {
    const $testElement = $('#sidebar');
    let $targetElement = $(e.target);
    do {
        if ($targetElement.get(0) === $testElement.get(0)) {
            return;
        }
        $targetElement = $targetElement.parent();
    } while ($targetElement.length);
    $testElement.removeClass('show');
});
