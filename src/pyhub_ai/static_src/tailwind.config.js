/**
 * This is a minimal config.
 * For a full list of options, see https://tailwindcss.com/docs/configuration
 */

module.exports = {
  /* tailwind css 클래스명을 사용한 소스 파일의 경로 패턴 */
  content: ["../**/forms.py", "../templates/**/*.html", "../static/**/*.js"],

  /* tailwind css 플러그인 */
  plugins: [
    require("@tailwindcss/forms"),
    require("@tailwindcss/typography"),
    require("@tailwindcss/aspect-ratio"),
    require("daisyui"),
  ],

  /* tailwind css 테마 설정 */
  theme: {
    extend: {
      // https://github.com/tailwindlabs/tailwindcss-typography#customizing-the-css
      typography: (theme) => ({
        DEFAULT: {
          // Custom CSS here ↓
          css: {
            ul: {
              marginTop: "0",
              marginBottom: "0",
            },
            li: {
              marginTop: "0",
              marginBottom: "0",
            },
            "li > *": {
              marginTop: "0",
              marginBottom: "0",
            },
            p: {
              marginTop: ".2em",
              marginBottom: ".2em",
            },
          },
        },
      }),
    },
  },
  /* daisyui 설정 : https://daisyui.com/docs/config/ */
  daisyui: {
    // https://daisyui.com/docs/themes/
    themes: false,
  },
};
