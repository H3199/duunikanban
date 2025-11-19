import ReactDOM from "react-dom/client";
import App from "./App";
import { MantineProvider } from "@mantine/core";
import { ModalsProvider } from "@mantine/modals";
import { BrowserRouter } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "./queryClient";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <QueryClientProvider client={queryClient}>
    <MantineProvider
      withCssVariables
      theme={{
        colorScheme: "dark",
        primaryColor: "blue",
        defaultRadius: "md",

        globalStyles: (theme) => ({
          "*, *::before, *::after": {
            boxSizing: "border-box",
          },
          body: {
            margin: 0,
            padding: 0,
            backgroundColor: theme.colors.dark[8],
            color: theme.colors.gray[2],
            fontFamily: "Inter, system-ui, sans-serif",
          },
        }),
      }}
    >
      <ModalsProvider>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </ModalsProvider>
    </MantineProvider>
  </QueryClientProvider>,
);
