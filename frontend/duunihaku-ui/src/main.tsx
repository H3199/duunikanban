import ReactDOM from "react-dom/client";
import { MantineProvider, createTheme } from "@mantine/core";
import "@mantine/core/styles.css"; // 👈 important: brings in Mantine's global styles
import { BrowserRouter } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "./queryClient";
import App from "./App";

const theme = createTheme({
  primaryColor: "blue",
  defaultRadius: "md",
  // you can add other design tokens here if needed
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <QueryClientProvider client={queryClient}>
    <MantineProvider
      theme={theme}
      defaultColorScheme="dark" // 👈 this is the official v7 way
      withCssVariables
    >
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </MantineProvider>
  </QueryClientProvider>,
);
