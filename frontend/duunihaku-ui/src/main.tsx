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
        globalStyles: (theme) => ({
          body: {
            backgroundColor: theme.colors.dark[8],
            color: theme.white,
            margin: 0,
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
