"use client";

import { Box, Button, Card, Flex, Text, TextField } from "@radix-ui/themes";
import { ArrowLeftIcon } from "@radix-ui/react-icons";
import { useRouter } from "next/navigation";

export default function SignUpForm() {
  const router = useRouter();
  return (
    <Box>
      <Flex direction="column" align="center" justify="center" height="100vh">
        <Card>
          <Flex direction="column" align="center" justify="center" gap="3">
            <Flex direction="row" gap="3" align="center">
              <Button
                variant="ghost"
                onClick={() => router.back()}
                className="w-full sm:w-auto"
              >
                <ArrowLeftIcon />
              </Button>
              <Text as="div" size="5" weight="bold">
                Create Account
              </Text>
            </Flex>
            <TextField.Root placeholder="First Name"></TextField.Root>
            <TextField.Root placeholder="Last Name"></TextField.Root>
            <TextField.Root placeholder="Enter your email"></TextField.Root>
            <TextField.Root
              type="password"
              placeholder="Create password"
            ></TextField.Root>
            <Button size="3">Next</Button>
          </Flex>
        </Card>
      </Flex>
    </Box>
  );
}
