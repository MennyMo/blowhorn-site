/* Offline search for the /docs/ section.
 *
 * From Docsy v0.14.3 assets/js/offline-search.js (Apache-2.0), itself
 * adapted from code by Matt Walters. Two changes from upstream:
 * - the attribution comment no longer names a blog URL, because a shipped
 *   script may not reference another host (see the privacy page);
 * - results render in an inline box under the search field instead of a
 *   Bootstrap popover, because Bootstrap's JavaScript is not shipped
 *   (same reason). The index, the query, and the result entries are
 *   unchanged.
 */

(function ($) {
  'use strict';

  $(document).ready(function () {
    const $searchInput = $('.td-search input');

    //
    // Register handler
    //

    $searchInput.on('change', (event) => {
      render($(event.target));

      // Hide keyboard on mobile browser
      $searchInput.blur();
    });

    // Prevent reloading page by enter key on sidebar search.
    $searchInput.closest('form').on('submit', () => {
      return false;
    });

    //
    // Lunr
    //

    let idx = null; // Lunr index
    const resultDetails = new Map(); // Will hold the data for the search results (titles and summaries)

    // Set up for an Ajax call to request the JSON data file that is created by Hugo's build process
    $.ajax($searchInput.data('offline-search-index-json-src')).then((data) => {
      idx = lunr(function () {
        this.ref('ref');

        // If you added more searchable fields to the search index, list them here.
        // Here you can specify searchable fields to the search index - e.g. individual toxonomies for you project
        // With "boost" you can add weighting for specific (default weighting without boost: 1)
        this.field('title', { boost: 5 });
        this.field('categories', { boost: 3 });
        this.field('tags', { boost: 3 });
        // this.field('projects', { boost: 3 }); // example for an individual toxonomy called projects
        this.field('description', { boost: 2 });
        this.field('body');

        data.forEach((doc) => {
          this.add(doc);

          resultDetails.set(doc.ref, {
            title: doc.title,
            excerpt: doc.excerpt,
          });
        });
      });

      $searchInput.trigger('change');
    });

    const render = ($targetSearchInput) => {
      //
      // Dispose existing results
      //

      $('.td-offline-search-results').remove();

      //
      // Search
      //

      if (idx === null) {
        return;
      }

      const searchQuery = $targetSearchInput.val();
      if (searchQuery === '') {
        return;
      }

      const results = idx
        .query((q) => {
          const tokens = lunr.tokenizer(searchQuery.toLowerCase());
          tokens.forEach((token) => {
            const queryString = token.toString();
            q.term(queryString, {
              boost: 100,
            });
            q.term(queryString, {
              wildcard:
                lunr.Query.wildcard.LEADING | lunr.Query.wildcard.TRAILING,
              boost: 10,
            });
            q.term(queryString, {
              editDistance: 2,
            });
          });
        })
        .slice(0, $targetSearchInput.data('offline-search-max-results'));

      //
      // Make result html
      //

      const $box = $('<div>').addClass('td-offline-search-results');

      $box.append(
        $('<div>')
          .css({
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '1em',
          })
          .append(
            $('<span>').text('Search results').css({ fontWeight: 'bold' })
          )
          .append(
            $('<button>')
              .attr({ type: 'button', 'aria-label': 'Close search results' })
              .addClass('td-offline-search-results__close')
              .text('\u00d7')
              .on('click', () => {
                $targetSearchInput.val('');
                $box.remove();
              })
          )
      );

      const $searchResultBody = $('<div>').css({
        maxHeight: `calc(100vh - ${
          $targetSearchInput.offset().top - $(window).scrollTop() + 180
        }px)`,
        overflowY: 'auto',
      });
      $box.append($searchResultBody);

      if (results.length === 0) {
        $searchResultBody.append(
          $('<p>').text(`No results found for query "${searchQuery}"`)
        );
      } else {
        results.forEach((r) => {
          const doc = resultDetails.get(r.ref);
          const href =
            $searchInput.data('offline-search-base-href') +
            r.ref.replace(/^\//, '');

          const $entry = $('<div>').addClass('mt-4');

          $entry.append(
            $('<small>').addClass('d-block text-body-secondary').text(r.ref)
          );

          $entry.append(
            $('<a>')
              .addClass('d-block')
              .css({
                fontSize: '1.2rem',
              })
              .attr('href', href)
              .text(doc.title)
          );

          $entry.append($('<p>').text(doc.excerpt));

          $searchResultBody.append($entry);
        });
      }

      $targetSearchInput.after($box);
    };
  });
})(jQuery);
