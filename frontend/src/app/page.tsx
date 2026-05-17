import Link from 'next/link';

const highlights = [
  {
    title: 'БИБЛИЯ',
    text: 'Библия — Слово Божье, наш высший авторитет в вере и жизни.',
    action: 'ЧИТАТЬ ДАЛЕЕ',
    icon: (
      <svg viewBox='0 0 24 24' aria-hidden='true'>
        <path d='M3 5a2 2 0 0 1 2-2h6a3 3 0 0 1 3 3v13a3 3 0 0 0-3-3H5a2 2 0 0 0-2 2V5Zm18 0a2 2 0 0 0-2-2h-6a3 3 0 0 0-3 3v13a3 3 0 0 1 3-3h6a2 2 0 0 1 2 2V5Z' />
      </svg>
    ),
  },
  {
    title: 'ОБЩИНА',
    text: 'Мы — церковь, объединённая верой и любовью во Христе.',
    action: 'УЗНАТЬ БОЛЬШЕ',
    icon: (
      <svg viewBox='0 0 24 24' aria-hidden='true'>
        <path d='M16 11a4 4 0 1 0-3.999-4A4 4 0 0 0 16 11Zm-8 0A3 3 0 1 0 5 8a3 3 0 0 0 3 3Zm8 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4ZM8 13c-.3 0-.63.02-.97.05A5.5 5.5 0 0 1 10 17v2H2v-2c0-2.21 3.58-4 6-4Z' />
      </svg>
    ),
  },
  {
    title: 'СЛУЖЕНИЕ',
    text: 'Мы служим Богу, нашей церкви и людям вокруг нас.',
    action: 'ПРИНЯТЬ УЧАСТИЕ',
    icon: (
      <svg viewBox='0 0 24 24' aria-hidden='true'>
        <path d='m12 21-1.45-1.32C5.4 15.03 2 11.95 2 8.5 2 5.4 4.4 3 7.5 3c1.74 0 3.41.81 4.5 2.09A6 6 0 0 1 16.5 3C19.6 3 22 5.4 22 8.5c0 3.45-3.4 6.53-8.55 11.18L12 21Z' />
      </svg>
    ),
  },
  {
    title: 'МЕРОПРИЯТИЯ',
    text: 'Следите за предстоящими событиями и будьте с нами.',
    action: 'СМОТРЕТЬ ВСЕ',
    icon: (
      <svg viewBox='0 0 24 24' aria-hidden='true'>
        <path d='M19 4h-1V2h-2v2H8V2H6v2H5a2 2 0 0 0-2 2v13a3 3 0 0 0 3 3h13a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2Zm0 16H6a1 1 0 0 1-1-1V10h14v10Zm0-12H5V6h14v2Z' />
      </svg>
    ),
  },
];

export default function PublicHomePage() {
  return (
    <main className='site-shell'>
      <header className='site-header'>
        <div className='container nav-wrap'>
          <div className='brand'>
            <div className='brand-logo' aria-hidden='true'>
              ✝
            </div>
            <div>
              <p className='brand-title'>Баптисты</p>
              <p className='brand-subtitle'>ВЕРА · СЕМЬЯ · СЛУЖЕНИЕ</p>
            </div>
          </div>

          <nav className='main-nav' aria-label='Главное меню'>
            <a href='#' className='active'>
              ГЛАВНАЯ
            </a>
            <a href='#about'>О НАС</a>
            <a href='#'>УЧЕНИЕ</a>
            <a href='#'>НОВОСТИ</a>
            <a href='#'>МЕРОПРИЯТИЯ</a>
            <a href='#'>РЕСУРСЫ</a>
            <a href='#'>КОНТАКТЫ</a>
          </nav>

          <Link href='/dashboard' className='donate-btn'>
            ПОЖЕРТВОВАТЬ
          </Link>
        </div>
      </header>

      <section className='hero'>
        <div className='hero-overlay'>
          <div className='container hero-content'>
            <h1>Ибо так возлюбил Бог мир, что отдал Сына Своего Единородного...</h1>
            <p className='verse'>От Иоанна 3:16</p>
            <p className='hero-text'>
              Мы — христиане-баптисты, верующие в авторитет Библии, спасение по благодати через веру и призванные
              служить Богу и людям.
            </p>
            <div className='hero-actions'>
              <a href='#about' className='btn-primary'>
                УЗНАТЬ БОЛЬШЕ О НАС
              </a>
              <Link href='/holidays' className='btn-secondary'>
                ПОСЕТИТЬ БОГОСЛУЖЕНИЕ
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className='highlights'>
        <div className='container highlight-grid'>
          {highlights.map((item) => (
            <article className='highlight-card' key={item.title}>
              <div className='icon-wrap'>{item.icon}</div>
              <h2>{item.title}</h2>
              <p>{item.text}</p>
              <a href='#'>{item.action} →</a>
            </article>
          ))}
        </div>
      </section>

      <section className='about' id='about'>
        <div className='container about-grid'>
          <div>
            <h2>О нашей церкви</h2>
            <p>
              Мы стремимся быть верными учению Христа, укреплять верующих, проповедовать Евангелие и помогать
              нуждающимся.
            </p>
            <a href='#' className='btn-primary'>
              ПОДРОБНЕЕ О НАС
            </a>
          </div>
          <div className='about-image' role='img' aria-label='Собрание в церкви' />
        </div>
      </section>
    </main>
  );
}
