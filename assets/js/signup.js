// Progressive enhancement for the signup form (layouts/_shortcodes/signup-form.html):
// submit the form as JSON to the signup service and show an inline result.
// Without JavaScript the form posts to the service, which redirects to a
// thanks page. The form's own action is the API URL, so this script names
// no host itself.
(function () {
  var form = document.getElementById('signup-form');
  if (!form) return;
  var status = document.getElementById('signup-status');
  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var data = {};
    new FormData(form).forEach(function (value, key) {
      data[key] = value;
    });
    fetch(form.action, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(data),
    })
      .then(function (res) {
        return res.json().then(function (body) {
          return { res: res, body: body };
        });
      })
      .then(function (pair) {
        if (pair.res.ok && pair.body.ok) {
          form.reset();
          status.textContent = 'You are on the list.';
        } else {
          status.textContent = (pair.body && pair.body.error) || 'Something went wrong. Please try again.';
        }
      })
      .catch(function () {
        status.textContent = 'Something went wrong. Please try again.';
      });
  });
})();
