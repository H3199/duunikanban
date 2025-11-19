import { Title, Container } from "@mantine/core";
import { KanbanBoard } from "../components/KanbanBoard";

export default function HomePage() {
  return (
    <Container size="xl" py="xl">
      <Title order={2} mb="lg">
        Duunikanban
      </Title>
      <KanbanBoard />
    </Container>
  );
}
