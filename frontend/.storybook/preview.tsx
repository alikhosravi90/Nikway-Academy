import type { Preview } from "@storybook/react-vite";
import "@fontsource-variable/vazirmatn";
import "../src/design.css";
const preview: Preview = {
  globalTypes: {
    theme: { description: "Theme", toolbar: { items: ["light", "dark"] } },
    locale: { description: "Direction", toolbar: { items: ["fa", "en"] } },
    variant: {
      description: "Design variant",
      toolbar: { items: ["jade", "ink", "paper"] },
    },
  },
  initialGlobals: { theme: "light", locale: "fa", variant: "jade" },
  decorators: [
    (Story, context) => {
      document.documentElement.dataset.theme = context.globals.theme;
      document.documentElement.dataset.variant = context.globals.variant;
      document.documentElement.dir =
        context.globals.locale === "fa" ? "rtl" : "ltr";
      document.documentElement.lang = context.globals.locale;
      return (
        <div className="workspace">
          <Story />
        </div>
      );
    },
  ],
  parameters: { layout: "fullscreen" },
};
export default preview;
