import { Title } from "@mantine/core";
import { KanbanBoard } from "../components/KanbanBoard";

export default function HomePage() {
  return (
    <div
      style={{
        width: "100%",
        padding: "2rem",
      }}
    >
      <Title order={2} mb="lg" style={{ color: "white", textAlign: "center" }}>
        Duunikanban
      </Title>

      <KanbanBoard />
    </div>
  );
}
