import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Text, Title, Button, ScrollArea, Loader } from "@mantine/core";

const API_URL = import.meta.env.VITE_API_URL;
export default function JobPage() {
  const { id } = useParams();

  const { data, isLoading } = useQuery({
    queryKey: ["job", id],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/api/v1/jobs/${id}`);
      return res.json();
    },
  });

  if (isLoading) return <Loader />;
  if (!data) return <>Job not found</>;

  return (
    <ScrollArea style={{ padding: "2rem" }}>
      <Title order={2}>{data.title}</Title>
      <Text size="lg" weight={500} mt="sm">
        {data.company}
      </Text>

      <Button
        component="a"
        href={data.url}
        target="_blank"
        mt="md"
        variant="light"
      >
        Open Job Posting
      </Button>

      <Text mt="xl" size="sm" style={{ whiteSpace: "pre-line" }}>
        {data.description || "No description available."}
      </Text>
    </ScrollArea>
  );
}
