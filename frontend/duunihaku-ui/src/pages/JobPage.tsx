import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Text,
  Title,
  Button,
  ScrollArea,
  Loader,
  Group,
  Badge,
  Textarea,
} from "@mantine/core";
import { useState, useEffect } from "react";
import { updateJobState, updateNotes } from "../api/jobsApi";

const API_URL = import.meta.env.VITE_API_URL;

export default function JobPage() {
  const { id } = useParams();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["job", id],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/api/v1/jobs/${id}`);
      if (!res.ok) throw new Error("Failed to fetch job");
      return res.json();
    },
  });

  // ---- Notes state ----
  const [localNotes, setLocalNotes] = useState("");

  // Sync once job data loads
  useEffect(() => {
    if (data?.notes) {
      setLocalNotes(data.notes);
    }
  }, [data]);

  // ---- Mutation: update job state ----
  const stateMutation = useMutation({
    mutationFn: ({ state }: { state: string }) => updateJobState(id!, state),
    onSuccess: () => {
      queryClient.invalidateQueries(["job", id]);
      queryClient.invalidateQueries(["jobs"]);
    },
  });

  // ---- Mutation: update notes ----
  const notesMutation = useMutation({
    mutationFn: ({ notes }: { notes: string }) => updateNotes(id!, notes),
    onSuccess: () => {
      queryClient.invalidateQueries(["job", id]);
      queryClient.invalidateQueries(["jobs"]);
    },
  });

  if (isLoading) return <Loader />;
  if (!data) return <>Job not found</>;

  return (
    <ScrollArea style={{ padding: "2rem" }}>
      <Title order={2}>{data.title}</Title>

      <Group mt="xs">
        <Text size="lg" weight={500}>
          {data.company}
        </Text>
        <Badge variant="filled" color="blue">
          {data.state?.toUpperCase() ?? "NEW"}
        </Badge>
      </Group>

      <Button
        component="a"
        href={data.url}
        target="_blank"
        mt="md"
        variant="light"
      >
        Open Job Posting
      </Button>

      {/* ---- ACTION BUTTON ROW ---- */}
      <Group mt="lg">
        <Button
          color="yellow"
          onClick={() => stateMutation.mutate({ state: "saved" })}
          disabled={stateMutation.isPending}
        >
          Save
        </Button>

        <Button
          color="green"
          onClick={() => stateMutation.mutate({ state: "applied" })}
          disabled={stateMutation.isPending}
        >
          Applied
        </Button>

        <Button
          color="red"
          variant="outline"
          onClick={() => stateMutation.mutate({ state: "trash" })}
          disabled={stateMutation.isPending}
        >
          Trash
        </Button>
      </Group>

      {/* ---- NOTES ---- */}
      <Title order={4} mt="xl">
        Notes
      </Title>

      <Textarea
        minRows={4}
        autosize
        placeholder="Add notes..."
        value={localNotes}
        onChange={(e) => setLocalNotes(e.target.value)}
        styles={{
          input: {
            background: "#1f1f1f",
            color: "white",
          },
        }}
      />

      <Group mt="sm">
        <Button
          size="sm"
          variant="filled"
          color="teal"
          disabled={
            notesMutation.isPending || localNotes === (data.notes ?? "")
          }
          onClick={() => notesMutation.mutate({ notes: localNotes })}
        >
          {notesMutation.isPending ? "Saving..." : "Save Notes"}
        </Button>

        {localNotes !== (data.notes ?? "") && !notesMutation.isPending && (
          <Text size="xs" style={{ opacity: 0.6 }}>
            Unsaved changes…
          </Text>
        )}
      </Group>

      <Text mt="xl" size="sm" style={{ whiteSpace: "pre-line" }}>
        {data.description || "No description available."}
      </Text>
    </ScrollArea>
  );
}
