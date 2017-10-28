import React from 'react';

/**
 * Home page component
 **/
export default function HomePage() {
  return (
      <div className="column">
        <h1>Bus shaming</h1>
        <p>
This site was created to answer the eternal question: Is the 370 bus really the worst bus in Sydney?
By 'worst' I mean that it's most frequently late and unreliable.
There have been <a href="http://www.dailytelegraph.com.au/newslocal/central-sydney/sydneys-bus-370-attracts-more-complaints-than-ever/news-story/440afcf40f1f6fc58551905e5495bf7e">multiple</a> <a href="http://www.dailytelegraph.com.au/newslocal/central-sydney/passengers-revolt-against-sydneys-laterunning-370-bus/news-story/7a1e106570dc4faa150cb80ad69dcbf5">news articles</a> about it, there's a <a href="https://www.facebook.com/groups/2262028391/">Facebook community</a> around it.
        </p>
        <p>
This site is a work in progress, but the ultimate goal is to publish statistics collected from Transport NSW and aggregated over time.
Once the stats come in, we'll be able to answer not only if there is a bus worse than the 370 but also if third-party agencies provided better or worse service than the government owned bus services.
        </p>
        <p>
If you're interested in helping out with this project, check it out on GitHub.
Web design skills are lacking (as you can see) and data science skills would be a huge bonus.
        </p>
      </div>
  );
};
