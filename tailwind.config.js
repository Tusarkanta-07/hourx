/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html"
  ],
  theme: {
    extend: {
      colors: {
        "primary-fixed": "#dde1ff",
        "surface-tint": "#b8c4ff",
        "primary-fixed-dim": "#b8c4ff",
        "on-background": "#dee1f9",
        "inverse-surface": "#dee1f9",
        "secondary-fixed-dim": "#3cddc7",
        "on-error-container": "#ffdad6",
        "on-tertiary": "#68000f",
        "on-secondary-fixed": "#00201c",
        "inverse-on-surface": "#2b3041",
        "surface-dim": "#0e1323",
        "tertiary-fixed-dim": "#ffb3b0",
        "surface-container-high": "#25293a",
        "on-surface": "#dee1f9",
        "on-tertiary-fixed": "#410006",
        "error": "#ffb4ab",
        "tertiary-fixed": "#ffdad8",
        "inverse-primary": "#3755c3",
        "outline-variant": "#444653",
        "primary": "#b8c4ff",
        "on-secondary": "#003731",
        "surface-container-highest": "#2f3446",
        "surface-container": "#1a1f30",
        "on-secondary-fixed-variant": "#005047",
        "primary-container": "#1e40af",
        "surface-container-lowest": "#080d1d",
        "on-primary-fixed": "#001453",
        "on-tertiary-container": "#ffa29e",
        "on-error": "#690005",
        "secondary-container": "#03c6b2",
        "surface-bright": "#34394a",
        "on-secondary-container": "#004d44",
        "tertiary": "#ffb3b0",
        "secondary": "#44e2cd",
        "secondary-fixed": "#62fae3",
        "on-primary": "#002584",
        "on-surface-variant": "#c4c5d5",
        "tertiary-container": "#921a23",
        "background": "#0e1323",
        "surface": "#0e1323",
        "on-tertiary-fixed-variant": "#8c1520",
        "on-primary-container": "#a8b8ff",
        "surface-container-low": "#161b2b",
        "on-primary-fixed-variant": "#173bab",
        "outline": "#8e909f",
        "surface-variant": "#2f3446",
        "error-container": "#93000a"
      },
      borderRadius: {
        "DEFAULT": "0.25rem",
        "lg": "0.5rem",
        "xl": "0.75rem",
        "full": "9999px"
      },
      spacing: {
        "gutter": "24px",
        "margin": "48px",
        "sm": "16px",
        "xs": "8px",
        "lg": "32px",
        "xl": "48px",
        "md": "24px"
      },
      fontFamily: {
        "headline-lg": ["Space Grotesk"],
        "display-2xl": ["Space Grotesk"],
        "headline-md": ["Space Grotesk"],
        "body-lg": ["Manrope"],
        "display-xl": ["Space Grotesk"],
        "body-md": ["Manrope"],
        "label-md": ["Manrope"]
      },
      fontSize: {
        "headline-lg": ["32px", { lineHeight: "1.3", fontWeight: "600" }],
        "display-2xl": ["72px", { lineHeight: "1.1", letterSpacing: "-0.04em", fontWeight: "700" }],
        "headline-md": ["24px", { lineHeight: "1.4", fontWeight: "600" }],
        "body-lg": ["18px", { lineHeight: "1.6", fontWeight: "400" }],
        "display-xl": ["48px", { lineHeight: "1.2", letterSpacing: "-0.02em", fontWeight: "700" }],
        "body-md": ["16px", { lineHeight: "1.6", fontWeight: "400" }],
        "label-md": ["14px", { lineHeight: "1", letterSpacing: "0.05em", fontWeight: "600" }]
      }
    }
  },
  plugins: [require("@tailwindcss/forms"), require("@tailwindcss/container-queries")]
};
